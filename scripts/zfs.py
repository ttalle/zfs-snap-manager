# Copyright (c) 2014 Kenneth Henderick <kenneth@ketronic.be>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Provides basic ZFS functionality
"""

from helper import Helper


class ZFS(object):
    """
    Contains generic ZFS functionality
    """

    @staticmethod
    def get_snapshots(volume='', endpoint=''):
        """
        Retreives a list of snapshots
        """

        if endpoint == '':
            command = 'zfs list -H -s creation -t snapshot{0}{1} || true'
        else:
            command = '{0} \'zfs list -H -s creation -t snapshot{1} || true\''
        if volume == '':
            volume_filter  = ''
        else:
            volume_filter = ' | grep {0}@'.format(volume)
        output = Helper.run_command(command.format(endpoint, volume_filter), '/')
        snapshots = {}
        for line in filter(len, output.split('\n')):
            parts = filter(len, line.split('\t'))
            volumename = parts[0].split('@')[0]
            if volumename not in snapshots:
                snapshots[volumename] = []
            snapshots[volumename].append(parts[0].split('@')[1])
        return snapshots

    @staticmethod
    def get_volumes():
        """
        Retreives all volumes
        """

        output = Helper.run_command('zfs list -H', '/')
        volumes = []
        for line in filter(len, output.split('\n')):
            parts = filter(len, line.split('\t'))
            volumes.append(parts[0])
        return volumes

    @staticmethod
    def snapshot(volume, name):
        """
        Takes a snapshot
        """

        command = 'zfs snapshot {0}@{1}'.format(volume, name)
        Helper.run_command(command, '/')

    @staticmethod
    def replicate(volume, base_snapshot, last_snapshot, target, endpoint=''):
        """
        Replicates a volume towards a given endpoint/target
        """

        delta = ''
        if base_snapshot is not None:
            delta = '-i {0}@{1} '.format(volume, base_snapshot)

        if endpoint == '':
            # We're replicating to a local target
            command = 'zfs send {0}{1}@{2} | zfs receive -F {3}'
            command = command.format(delta, volume, last_snapshot, target)
            Helper.run_command(command, '/')
        else:
            # We're replicating to a remove server
            command = 'zfs send {0}{1}@{2} | mbuffer -q -v 0 -s 128k -m 512M | {3} \'mbuffer -s 128k -m 512M | zfs receive -F {4}\''
            command = command.format(delta, volume, last_snapshot, endpoint, target)
            Helper.run_command(command, '/')

    @staticmethod
    def destroy(volume, snapshot):
        """
        Destroyes a volume
        """

        command = 'zfs destroy {0}@{1}'.format(volume, snapshot)
        Helper.run_command(command, '/')
