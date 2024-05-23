from sqlalchemy import create_engine

#SQLALCHEMY_DATABASE_URL = "mysql://root:@localhost/easysearch"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://psiubebidas.com.br_multiservices:95m3D7Yx3u5LYLwY@194.195.92.137/psiubebidas.com.br_multiservices"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=50, pool_timeout=1000)


