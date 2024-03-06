

def classFactory(iface):
  from .geonaturegisPlugin import pluginGeonatGIS
  return pluginGeonatGIS(iface)

