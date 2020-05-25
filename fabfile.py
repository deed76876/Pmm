import tempfile

from fabric2 import Connection, task


host = "deploy@workbench.feinheit.ch"
installations = ["fh", "dbpag", "bf", "test"]


@task
def check(c):
    c.run("venv/bin/flake8 .")
    c.run("yarn run check")


@task
def dev(c):
    with tempfile.NamedTemporaryFile("w+") as f:
        # https://gist.github.com/jiaaro/b2e1b7c705022c2cf56888152a999f65
        f.write(
            """\
trap "exit" INT TERM
trap "kill 0" EXIT

PYTHONWARNINGS=always venv/bin/python manage.py runserver 0.0.0.0:%(port)s &
HOST=%(host)s yarn run dev &

for job in $(jobs -p); do wait $job; done
"""
            % {"port": 8000, "host": "127.0.0.1"}
        )
        f.flush()

        c.run("bash %s" % f.name)


def _do_deploy(c, folder, rsync):
    with c.cd(folder):
        c.run("git checkout master")
        c.run("git fetch origin")
        c.run("git merge --ff-only origin/master")
        c.run('find . -name "*.pyc" -delete')
        c.run("venv/bin/pip install -U pip wheel setuptools")
        c.run("venv/bin/pip install -r requirements.txt")
        for wb in installations:
            c.run("DOTENV=.env/{} venv/bin/python manage.py migrate".format(wb))
    if rsync:
        c.local("rsync -avz --delete static/ {}:{}static".format(host, folder))
    with c.cd(folder):
        c.run(
            "DOTENV=.env/{} venv/bin/python manage.py collectstatic --noinput".format(
                installations[0]
            ),
        )


def _restart_all(c):
    for wb in installations:
        c.run("systemctl --user restart workbench@{}".format(wb), echo=True)


@task
def deploy(c):
    check(c)
    c.run("git push origin master")
    c.run("yarn run prod")
    with Connection(host, forward_agent=True) as c:
        _do_deploy(c, "www/workbench/", rsync=True)
        _restart_all(c)


@task
def deploy_code(c):
    check(c)
    c.run("git push origin master")
    with Connection(host, forward_agent=True) as c:
        _do_deploy(c, "www/workbench/", rsync=False)
        _restart_all(c)


@task
def pull_db(c, namespace):
    remote = {"fh": "workbench", "dbpag": "dbpag-workbench", "bf": "bf-workbench"}[
        namespace
    ]
    c.run("dropdb --if-exists workbench")
    c.run("createdb workbench")
    c.run(
        'ssh -C root@workbench.feinheit.ch "sudo -u postgres pg_dump -Ox %s"'
        " | psql workbench" % remote,
    )


@task
def dump_db(c, namespace):
    remote = {"fh": "workbench", "dbpag": "dbpag-workbench", "bf": "bf-workbench"}[
        namespace
    ]
    c.run(
        'ssh -C root@workbench.feinheit.ch "sudo -u postgres pg_dump -Ox %s"'
        " > tmp/%s.sql" % (remote, remote),
    )


@task
def load_db(c, path):
    c.run("dropdb --if-exists workbench")
    c.run("createdb workbench")
    c.run("psql workbench < %s" % path)


@task
def mm(c):
    c.run(
        "PATH=/usr/bin:/usr/sbin "
        "venv/bin/python manage.py makemessages -a -i venv -i htmlcov"
        " --add-location file",
    )
    c.run(
        "PATH=/usr/bin:/usr/sbin "
        "venv/bin/python manage.py makemessages -a -i venv -i htmlcov"
        " --add-location file"
        " -i node_modules -i lib"
        " -d djangojs",
    )


@task
def cm(c):
    c.run(
        "cd conf &&"
        " PATH=/usr/bin:/usr/sbin ../venv/bin/python ../manage.py compilemessages"
    )


@task
def update_requirements(c):
    c.run("rm -rf venv")
    c.run("python3 -m venv venv")
    c.run("venv/bin/pip install -U pip wheel setuptools")
    c.run("venv/bin/pip install -U -r requirements-to-freeze.txt --pre")
    freeze(c)


@task
def freeze(c):
    c.run(
        '(printf "# AUTOGENERATED, DO NOT EDIT\n\n";'
        "venv/bin/pip freeze -l"
        # Until Ubuntu gets its act together:
        ' | grep -vE "(^pkg-resources)"'
        ") > requirements.txt",
    )


@task
def setup(c):
    c.run("python3 -m venv venv")
    update(c)


@task
def update(c):
    c.run("venv/bin/pip install -U pip wheel")
    c.run("venv/bin/pip install -r requirements.txt")
    c.run("yarn")
    c.run("venv/bin/python manage.py migrate")
