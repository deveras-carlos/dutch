from random import randint

class Game:
    class Player:
        def __init__( self, id : str, table_size : int ):
            self.id : str = id
            self.ready : bool = False
            self.deck : dict[ tuple[ int ], int ] = dict(  )
            self.table : list[ tuple[ int ] ] = [ None for _ in range( table_size ) ]
            self.last_bought_card : tuple = None
    
    def __init__( self ):
        self.observers : set = set(  )
        self.players : dict[ str, self.Player ] = dict(  )
        self.play_order : list[ str ] = list(  )
        self.current_turn : int = None
        
        self.amt_card_start_deck : int = 5
        self.player_table_size : int = 12

        self.last_winner : str = None
        self.top_card : str = None
        self.last_discard : str = None

    def start( self ):
        if not all( player.ready for player in self.players.values(  ) ):
            return
        
        for player in self.players.values(  ):
            for _ in range( self.amt_card_start_deck ):
                suit = randint( 1, 4 )
                number = randint( 1, 3 )
                if player.deck.get( ( suit, number ) ):
                    player.deck[ ( suit, number ) ] += 1
                else:
                    player.deck[ ( suit, number ) ] = 0
        
        if self.last_winner:
            self.current_turn = self.last_winner
        else:
            self.current_turn = randint( len( self.players ) - 1 )

    def subscribe( self, observer ) -> None:
        self.observers.add( observer )
    
    def notify_all( self, command : dict ) -> None:
        for observer in self.observers:
            observer.update( command )
    
    def set_state( self, new_state : dict ) -> None:
        self.players = new_state[ "players" ]

    def add_player( self, command : dict ) -> None:
        player_id = command[ "player_id" ]

        self.players[ player_id ] = self.Player( player_id )
        self.play_order.append( player_id )

        self.notify_all({
            "type" : "add_player",
            "player_id" : player_id
        })
    
    def remove_player( self, command : dict ) -> None:
        player_id = command[ "player_id" ]

        del self.players[ player_id ]

        self.notify_all({
            "type" : "remove_player",
            "player_id" : player_id
        })
    
    def player_command( self, command : dict ) -> None:
        self.notify_all( command )

        def buy_card( player : self.Player, erroneous_discard : bool = False ) -> None:
            if not erroneous_discard and player.id != self.play_order[ self.current_turn ]:
                return
            suit = randint( 1, 4 )
            number = randint( 1, 3 )

            self.notify_all({
                "type" : "card_bought",
                "player_id" : player.id
            })

            player.last_bought_card = ( suit, number )

        def discard_card( player : self.Player, suit : int, number : int, table_pos : int = None ) -> None:
            if not player.id == self.play_order[ self.current_turn ]:
                if self.last_discard == player.id or \
                        suit != self.top_card[ 0 ] or number != self.top_card[ 1 ]:
                    player.table[ table_pos ] = None
                    self.notify_all({
                        "type" : "erroneous_discard",
                        "player_id" : player.id,
                        "suit" : suit,
                        "number" : number
                    })
                    return
            
            self.notify_all({
                "type" : "discard",
                "player_id" : player.id,
                "suit" : suit,
                "number" : number
            })

        def swap_card( player : self.Player, table_pos : int, suit : int, number : int ) -> None:
            if not player.id == self.play_order[ self.current_turn ]:
                return
            if player.table[ table_pos ] is None:
                self.notify_all({
                    "type" : "invalid_swap",
                    "player_id" : player.id,
                    "suit" : suit,
                    "number" : number
                })
                return
            card_to_discard = player.table[ table_pos ]
            player.table[ table_pos ] = ( suit, number )
            self.notify_all({
                "type" : "successful_swap",
                "player_id" : player.id
            })
        
        accepted_actions = {
            ""
        }

        input_data = command[ "input_data" ]
        player_id = command[ "player_id" ]
        player = self.players[ player_id ]
        action_function = accepted_actions[ input_data ]

        if ( player and action_function ):
            action_function( player )