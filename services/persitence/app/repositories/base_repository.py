from database import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, text, select, desc

class BaseRepository:
    def __init__( self, model ):
        self.model = model
    
    def save( self, entity ):
        try:
            db.session.add( entity )
            db.session.commit(  )
            return entity
        except SQLAlchemyError as e:
            db.session.rollback(  )
            raise e

    def get_by_id( self, id ):
       
        query = db.session.execute(
            select( self.model ).where(
                self.model.id == id
            )
        )
        return query.scalars(  ).first(  )

    def update(self, entity, **kwargs):
        try:
            if not entity:
                raise ValueError("Nenhuma entidade foi passada para atualização.")

            for attr, value in kwargs.items():
                if hasattr(entity, attr):
                    setattr(entity, attr, value)
                else:
                    raise ValueError(f"Entidade não possui atributo {attr}")

            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
        except ValueError as e:
            db.session.rollback()
            raise e

    def delete( self, entity ):
        try:
            db.session.delete( entity )
            db.session.commit(  )
            return entity
        except SQLAlchemyError as e:
            db.session.rollback(  )
            raise e

    def get_all(self, order_by: str = None):
        query = select(self.model)
        
        if order_by:
            column = getattr(self.model, order_by, None)
            if column is not None:
                query = query.order_by(desc(column))  # Ordenação decrescente
        
        result = db.session.execute(query)
        return result.scalars().all()

    def find_first_by( self, **kwargs ):
        condicoes = [ getattr( self.model, key ) == value for key, value in kwargs.items(  ) ]
        query = db.session.execute(
            select( self.model ).where( *condicoes )
        )
       
        return query.scalars(  ).first(  )

    def find_all_by(self, **kwargs):
        order_by = kwargs.pop("order_by", None)  # ordena de forma decrescente pelo campo passado no order_By
        ascending = kwargs.pop("ascending", False)  # Flag para determinar a ordem crescente ou decrescente
        condicoes = [getattr(self.model, key) == value for key, value in kwargs.items()]
        query = select(self.model).where(*condicoes)

        if order_by:
            column = getattr(self.model, order_by, None)
            if column is not None:
                if ascending:
                    query = query.order_by(asc(column))  # Ordenação crescente
                else:
                    query = query.order_by(desc(column))  # Ordenação decrescente

        result = db.session.execute(query)
        return result.scalars().all()


    def count( self ):
        query = db.session.execute( select( self.model ) )
        return query.fetchall(  ).count(  )
    
    def count_by( self, **kwargs ):
        query = db.session.execute( select( self.model ).filter_by( **kwargs ) )
        return query.fetchall(  ).count(  )
    
    def bulk_save( self, entities ):
        try:
            db.session.add_all( entities )
            db.session.commit(  )
            return entities
        except SQLAlchemyError as e:
            db.session.rollback(  )
            raise e
    
    def query_builder( self, **filters ):
        conditions = [ getattr( self.model, field )  == value for field, value in filters.items(  ) if hasattr( self.model, field ) ]
        query = db.session.execute( select( self.model ).where( *conditions ) )
        return query.scalars(  ).all(  )

    def execute_raw_sql( self, sql, params = None ):
        result = db.session.execute( text(  sql  ), params or { }  )
        db.session.commit(  )
        return result