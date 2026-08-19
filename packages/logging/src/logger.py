import logging, sys
from pythonjsonlogger import jsonlogger
def configure_logging(service: str):
    h=logging.StreamHandler(sys.stdout); h.setFormatter(jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s service'))
    root=logging.getLogger(); root.handlers=[h]; root.setLevel(logging.INFO); logging.LoggerAdapter(root, {'service': service}); return root
