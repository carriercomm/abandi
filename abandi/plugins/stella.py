from abandi import version
from abandi.cli import call
from abandi.exefinder import searchExe
from yapsy.IPlugin import IPlugin



class Stella(IPlugin):
    hook = 'runner'

    home_url = 'http://stella.sourceforge.net/'
    long_name='Stella'
    extensions=['bin']
    platforms=['atari2k6']
    ubuntu_package='stella'

    def run_game(self,game):
        (stdout,stderr,_) =call('stella %s' % searchExe(game.dir, game.name, self.extensions))
    def version(self):
        (stdout,stderr,_) =call('stella -help')
        return version.extract_version(stdout)
