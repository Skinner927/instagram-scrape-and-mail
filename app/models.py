from json import dumps
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum


Base = declarative_base()


class MediaTypeEnum(enum.Enum):
    video = 'video'
    image = 'image'


class MediaSourceEnum(enum.Enum):
    Instagram = 'instagram'
    Direct = 'direct'  # TODO: Implement
    Facebook = 'facebook'  # TODO: Implement


class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(MediaTypeEnum))  # video and movie
    source = Column(Enum(MediaSourceEnum))  # Instagram, Facebook, etc
    # Filename relative to IMG_DIR
    # Format: module_time-created_[username].extension
    file_path = Column(String(255), nullable=True)
    last_downloaded = Column(DateTime)
    # OFF enabled = Column(Boolean, default=True)

    # Joined table inheritance
    # http://docs.sqlalchemy.org/en/latest/orm/inheritance.html#joined-table-inheritance
    __mapper_args__ = {
        'polymorphic_identity': 'media',
        'polymorphic_on': source
    }
    # Maybe add this
    # http://stackoverflow.com/questions/14885042/in-sqlalchemy-how-can-i-use-polymorphic-joined-table-inheritance-when-the-child
    # inherit_condition=(point_id == pbx_point.id)

    def __repr__(self):
        return "<Media (type='%s', source='%s', last_downloaded='%s')>" % (
            self.type, self.source, self.last_downloaded)


class IgMedia(Media):
    __tablename__ = 'igMedia'

    # From Media:
    # id
    # type
    # source
    # file_path
    # last_downloaded
    # OFF enabled=true

    id = Column(Integer, ForeignKey('media.id'), primary_key=True)
    media_id = Column(String(35))
    url = Column(Text)
    json = Column(UnicodeText)
    user_id = Column(Integer, ForeignKey('igUsers.id'))
    user = relationship('IgUser', back_populates='media')

    __mapper_args__ = {
        'polymorphic_identity': MediaSourceEnum.Instagram,
    }

    def __init__(self, json, ig_user):
        self.media_id = json['id']
        if json['type'] == 'carousel':
            self.type = MediaTypeEnum['image']
        else:
            self.type = MediaTypeEnum[json['type']]
        self.source = MediaSourceEnum.Instagram
        self.url = json['url']
        self.json = dumps(json, ensure_ascii=False)
        self.user_id = ig_user.id
        self.user = ig_user

    def __repr__(self):
        return self.url


class IgUser(Base):
    __tablename__ = 'igUsers'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    full_name = Column(String(80), nullable=True)
    profile_picture_url = Column(String(255), nullable=True)
    initialized = Column(Boolean, default=False)
    media = relationship('IgMedia', back_populates='user')

    # @property
    # def img_dir(self):
    #     if not self.username:
    #         return None
    #     img_dir = config['settings']['working_dir']
    #     if not os.path.exists(img_dir):
    #         mkdirs(img_dir)
    #     return img_dir

    # def save_profile_pic(self):
    #     img_dir = self.img_dir
    #     if not dir or not self.profile_picture_url:
    #         return False
    #     extension = self.profile_picture_url.split('.')[-1]
    #     urllib.urlretrieve(self.profile_picture_url,
    #                        os.path.join(
    #                            img_dir,
    #                            'ig_profile_%s.%s' % (self.username, extension)
    #                        ))
    #     return True

    def __repr__(self):
        name = self.username
        if self.full_name:
            name += ': ' + self.full_name
        return name
