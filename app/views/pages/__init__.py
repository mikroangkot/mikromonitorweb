import importlib
import pkgutil
from pathlib import Path

class Pages:
	pass

pages_dir = Path(__file__).parent
for _, module_name, is_pkg in pkgutil.iter_modules([str(pages_dir)]):
	if not is_pkg:
		module = importlib.import_module(f"app.views.pages.{module_name}")
		if hasattr(module, module_name):
			func = getattr(module, module_name)
			setattr(Pages, module_name, staticmethod(func))
		else:
			for attr_name in dir(module):
				if attr_name.endswith("_view") and callable(getattr(module, attr_name)):
					func = getattr(module, attr_name)
					setattr(Pages, attr_name, staticmethod(func))