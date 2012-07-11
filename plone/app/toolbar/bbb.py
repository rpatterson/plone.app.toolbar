from lxml import html
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import ViewletBase

from plone.app.layout.globals.interfaces import IViewView


class IToolbarAlerts(IViewletManager):
    """A viewlet manager that renders alerts managed by the toolbar."""


class ToolbarViewlet(ViewletBase):

    def update(self):
        super(ToolbarViewlet, self).update()
        if IViewView.providedBy(self.__parent__):
            # Ensure this viewlet has the interface that the iterate
            # alert viewlets are registered against such that they
            # only show up on view, not on edit.
            alsoProvides(self, IViewView)

    def render(self):
        context, request = self.context, self.request
        tile = getMultiAdapter((context, request), name=u'plone.toolbar')

        tile_body = ''
        tree = html.fromstring(tile.index())
        for el in tree.body.getchildren():
            tile_body += html.tostring(el)

        resources = ';'.join(tile.resources())
        return (u'<div style="display:none;" ' + \
                    u'data-iframe="toolbar" ' + \
                    u'data-iframe-resources="%s">%s</div>' + \
                    u'\n<div data-iframe="toolbar-alerts" ' + \
                    u'data-iframe-resources="%s">%s</div>') % (
                        resources, tile_body, resources, self.index())


class NullViewlet(ViewletBase):
    """Simply view that renders an empty string.

    For BBB purposes, to disable certain viewlets, we register an override
    for the same name and context, specific to the ICMSUILayer layer, using
    this class to render nothing.
    """

    def render(self):
        return u""
