from os.path import dirname

import Testing
import App.config
cfg = App.config.getConfiguration()
cfg.testinghome = dirname(__file__)
