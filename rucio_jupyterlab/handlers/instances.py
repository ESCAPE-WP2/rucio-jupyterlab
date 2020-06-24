import json
import tornado
from rucio_jupyterlab.db import get_db
from .base import RucioAPIHandler


class InstancesHandler(RucioAPIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server

    @tornado.web.authenticated
    def get(self):
        db = get_db()  # pylint: disable=invalid-name
        active_instance = db.get_active_instance()
        instances = self.rucio_config.list_instances()
        self.finish(json.dumps({
            'active_instance': active_instance,
            'instances': instances
        }))

    @tornado.web.authenticated
    def put(self):
        json_body = self.get_json_body()
        picked_instance = json_body['instance']

        db = get_db()  # pylint: disable=invalid-name
        db.set_active_instance(picked_instance)

        self.finish(json.dumps({'success': True}))
