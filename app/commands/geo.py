import logging

from . import manager
from app import db
from app.models import (
    ConventionLocation,
    ConventionLocationDistance,
    )


logger = logging.getLogger(__name__)


@manager.command
def geo(rebuild=False):
    if rebuild:
        logger.info("Updating locations")
        for loc in ConventionLocation.query:
            try:
                loc.get_lat_lon()
            except:
                logger.error("Failed to get location for %s", loc, exc_info=True)
        db.session.commit()
        logger.info("Updating distances")
        ConventionLocationDistance._truncate_table()
        for loc in ConventionLocation.query:
            loc.get_distances()
            db.session.commit()
        logger.info("Done")
    else:
        logger.error("Nothing to do")
