#!/usr/bin/env python3
"""Freeze an explicit engine checkout; build without editing its go.mod or the suite's."""
import argparse, datetime, hashlib, io, json, os, pathlib, shutil, subprocess, sys, tarfile, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def command(args, cwd):
    if args[0] == 'git':
        args = ['git', '-c', 'safe.directory=' + str(cwd)] + args[1:]
    return subprocess.check_output(args, cwd=cwd)

def files(root):
    return sorted(set(x for x in command(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], root).decode().split('\0') if x))

def snapshot(root, paths, dest=None):
    h = hashlib.sha256(); manifest = []
    for name in paths:
        path = root / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        h.update(name.encode() + b'\0' + len(data).to_bytes(8, 'big') + data)
        manifest.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
        if dest:
            target = dest / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return h.hexdigest(), manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True, type=pathlib.Path)
    parser.add_argument('--ref', help='freeze this exact engine Git commit instead of its working tree')
    parser.add_argument('--results', type=pathlib.Path, default=ROOT / 'results' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    args, flags = parser.parse_known_args()
    if flags and flags[0] == '--': flags = flags[1:]
    engine = args.engine.resolve(); out = args.results.resolve()
    if not (engine / 'go.mod').is_file(): parser.error('--engine must name an Argon source checkout')
    out.mkdir(parents=True, exist_ok=False)
    engine_head = command(['git', 'rev-parse', '--verify', '--end-of-options', (args.ref or 'HEAD') + '^{commit}'], engine).decode().strip()
    patch = b'' if args.ref else command(['git', 'diff', '--binary', 'HEAD'], engine)
    (out / 'engine.patch').write_bytes(patch)
    engine_paths = [] if args.ref else files(engine)
    suite_paths = [p for p in files(ROOT) if p.endswith('.go') or p in ('go.mod', 'go.sum', 'Dockerfile', 'docker-compose.yml') or p.startswith('scripts/')]
    suite_hash, suite_manifest = snapshot(ROOT, suite_paths)
    with tempfile.TemporaryDirectory(prefix='argonbench-source-') as temp:
        tmp = pathlib.Path(temp); frozen = tmp / 'engine'; frozen.mkdir()
        if args.ref:
            data = command(['git', 'archive', engine_head], engine)
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                archive.extractall(frozen, filter='data')
            engine_paths = sorted(str(p.relative_to(frozen)) for p in frozen.rglob('*') if p.is_file())
            engine_hash, engine_manifest = snapshot(frozen, engine_paths)
        else:
            engine_hash, engine_manifest = snapshot(engine, engine_paths, frozen)
            # A second read detects changes while copying; reject an incoherent snapshot.
            check_hash, _ = snapshot(engine, engine_paths)
            if (check_hash != engine_hash or files(engine) != engine_paths
                    or command(['git', 'diff', '--binary', 'HEAD'], engine) != patch
                    or command(['git', 'rev-parse', 'HEAD'], engine).decode().strip() != engine_head):
                raise RuntimeError('engine changed while freezing; retry after edits settle')
        frozen_suite = tmp / 'suite'; frozen_suite.mkdir()
        check_suite_hash, _ = snapshot(ROOT, suite_paths, frozen_suite)
        if check_suite_hash != suite_hash:
            raise RuntimeError('suite changed while freezing; retry after edits settle')
        provenance = {
            'kind': 'committed-engine-source' if args.ref else 'unpublished-source-snapshot',
            'captured_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'engine': {'original_path': str(engine), 'git_head': engine_head, 'git_branch': '' if args.ref else command(['git','branch','--show-current'],engine).decode().strip(), 'dirty': False if args.ref else bool(command(['git','status','--porcelain'],engine)), 'tracked_diff_sha256': hashlib.sha256(patch).hexdigest(), 'source_sha256': engine_hash, 'manifest': engine_manifest},
            'suite': {'git_head': command(['git','rev-parse','HEAD'],ROOT).decode().strip(), 'dirty': bool(command(['git','status','--porcelain'],ROOT)), 'executable_source_sha256': suite_hash, 'manifest': suite_manifest},
            'build': {'method': 'Go module replace to frozen exact engine source; no source changes during measurement', 'go_version': command(['go','version'],ROOT).decode().strip()},
            'command': [sys.executable, str(pathlib.Path(__file__).resolve()), '--engine', str(engine), '--results', str(out)] + (['--ref', engine_head] if args.ref else []) + ['--'] + flags,
        }
        (out / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
        # Archive the exact source, including untracked implementation files absent from engine.patch.
        shutil.make_archive(str(out / 'engine-source'), 'gztar', frozen)
        shutil.make_archive(str(out / 'suite-source'), 'gztar', frozen_suite)
        modfile = tmp / 'bench.mod'; shutil.copy2(frozen_suite/'go.mod',modfile); shutil.copy2(frozen_suite/'go.sum',tmp/'bench.sum')
        subprocess.run(['go','mod','edit','-modfile',str(modfile),'-replace','github.com/argon-lab/argon='+str(frozen)],cwd=frozen_suite,check=True)
        common = ['-mod=mod','-modfile',str(modfile)]
        subprocess.run(['go','test',*common,'.'],cwd=frozen_suite,check=True)
        binary = tmp / 'argonbench'
        subprocess.run(['go','build',*common,'-o',str(binary),'.'],cwd=frozen_suite,check=True)
        provenance['build']['binary_sha256'] = hashlib.sha256(binary.read_bytes()).hexdigest()
        provenance['build']['module_info'] = command(['go','version','-m',str(binary)],ROOT).decode()
        (out / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
        subprocess.run([str(binary),'-provenance',str(out/'provenance.json'),'-out',str(out/'report.md'),'-json',str(out/'raw.json'),*flags],cwd=ROOT,check=True)
    print(out)

if __name__ == '__main__':
    main()
