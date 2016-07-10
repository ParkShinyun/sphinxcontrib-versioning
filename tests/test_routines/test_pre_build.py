"""Test function in module."""

import py

from sphinxcontrib.versioning.routines import gather_git_info, pre_build
from sphinxcontrib.versioning.versions import Versions


def test_single(local_docs):
    """With single version.

    :param local_docs: conftest fixture.
    """
    remotes = gather_git_info(str(local_docs), ['conf.py'])[1]
    versions = Versions(remotes)
    assert len(versions) == 1

    # Run and verify directory.
    exported_root = py.path.local(pre_build(str(local_docs), versions, 'master', list()))
    assert len(exported_root.listdir()) == 1
    assert exported_root.join(versions['master']['sha'], 'conf.py').read() == ''

    # Verify versions URLs.
    expected = ['contents.html']
    assert sorted(r['url'] for r in versions.remotes) == expected


def test_dual(local_docs, run):
    """With two versions, one with master_doc defined.

    :param local_docs: conftest fixture.
    :param run: conftest fixture.
    """
    run(local_docs, ['git', 'checkout', 'feature'])
    local_docs.join('conf.py').write('master_doc = "index"\n')
    local_docs.join('index.rst').write(
        'Test\n'
        '====\n'
        '\n'
        'Sample documentation.\n'
    )
    run(local_docs, ['git', 'add', 'conf.py', 'index.rst'])
    run(local_docs, ['git', 'commit', '-m', 'Adding docs with master_doc'])
    run(local_docs, ['git', 'push', 'origin', 'feature'])

    remotes = gather_git_info(str(local_docs), ['conf.py'])[1]
    versions = Versions(remotes)
    assert len(versions) == 2

    # Run and verify directory.
    exported_root = py.path.local(pre_build(str(local_docs), versions, 'master', list()))
    assert len(exported_root.listdir()) == 2
    assert exported_root.join(versions['master']['sha'], 'conf.py').read() == ''
    assert exported_root.join(versions['feature']['sha'], 'conf.py').read() == 'master_doc = "index"\n'

    # Verify versions URLs.
    expected = ['contents.html', 'feature/index.html']
    assert sorted(r['url'] for r in versions.remotes) == expected


def test_file_collision(local_docs, run):
    """Test handling of filename collisions between generates files from root ref and branch names.

    :param local_docs: conftest fixture.
    :param run: conftest fixture.
    """
    run(local_docs, ['git', 'checkout', '-b', '_static'])
    run(local_docs, ['git', 'push', 'origin', '_static'])

    remotes = gather_git_info(str(local_docs), ['conf.py'])[1]
    versions = Versions(remotes)
    assert len(versions) == 2

    # Run and verify URLs.
    pre_build(str(local_docs), versions, 'master', list())
    expected = ['_static_/contents.html', 'contents.html']
    assert sorted(r['url'] for r in versions.remotes) == expected


def test_invalid_name(local_docs, run):
    """Test handling of branch names with invalid URL characters.

    :param local_docs: conftest fixture.
    :param run: conftest fixture.
    """
    run(local_docs, ['git', 'checkout', '-b', 'robpol86/feature'])
    run(local_docs, ['git', 'push', 'origin', 'robpol86/feature'])

    remotes = gather_git_info(str(local_docs), ['conf.py'])[1]
    versions = Versions(remotes)
    assert len(versions) == 2

    # Run and verify URLs.
    pre_build(str(local_docs), versions, 'master', list())
    expected = ['contents.html', 'robpol86_feature/contents.html']
    assert sorted(r['url'] for r in versions.remotes) == expected
