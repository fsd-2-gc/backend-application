# Re-export views so existing imports and handler paths keep working
from .health import health
from .getproducts import getproducts
from .errors import error_400, error_404, error_500
