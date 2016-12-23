from models import *
from sqlalchemy.orm import sessionmaker
from config import config

_session = None
_engine = None


def get_session():
    global _session, _engine
    if not _session:
        sqlite_location = 'sqlite:///%s' % config['settings']['db']
        _engine = create_engine(sqlite_location)
        Session = sessionmaker(bind=_engine)
        _session = Session()
        Base.metadata.create_all(_engine)
        _session.commit()

    return _session


def close_database():
    global _session, _engine

    if _session:
        _session.close()
    _session = None

    if _engine:
        _engine.dispose()
    _engine = None


def commit():
    get_session().commit()


def get_or_create_ig_user(username):
    session = get_session()
    ig_user = session.query(IgUser).filter(
        IgUser.username == username).first()
    if not ig_user:
        ig_user = IgUser(username=username)
        session.commit()

    return ig_user


def create_ig_media_if_not_exist(media, ig_user):
    """

    :param media:
    :param ig_user:
    :return: False if not new media else the new media object
    """
    session = get_session()
    media_in_db = session.query(IgMedia).filter(
        IgMedia.user_id == ig_user.id,
        IgMedia.media_id == media['id']).first()

    if media_in_db:
        return False

    # Create new
    ig_media = IgMedia(media, ig_user)

    session.add(ig_media)
    session.commit()

    return ig_media
