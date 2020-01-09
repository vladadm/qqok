#!python3
# -*- coding: utf-8 -*-


#client_keys=['/Users/noilk/.ssh/id_rsa', '/Users/noilk/.ssh/id_rsa.pub'])

import asyncio, asyncssh

async def run_client(host, command):
    #asyncssh.import_known_hosts("{0} {1}".format('core-db-shard14-dbm01b.prod.core.amosrv.ru', '/Users/noilk/.ssh/id_rsa.pub'))
    async with asyncssh.connect(host) as conn:
        return await conn.run(command)

async def run_multiple_clients():
    # Put your lists of hosts here
    hosts = ['dns-pri01a.infra.dns.amosrv.ru',
             'dns-pri01b.infra.dns.amosrv.ru',
             ]

    tasks = (run_client(host, 'sudo puppet agent -t') for host in hosts)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print('Task %d failed: %s' % (i, str(result)))
        elif result.exit_status != 0:
            print('Task %d exited with status %s:' % (i, result.exit_status))
            print(result.stderr, end='')
        else:
            print('Task %d succeeded:' % i)
            print(result.stdout, end='')

        print(75*'-')

asyncio.get_event_loop().run_until_complete(run_multiple_clients())
