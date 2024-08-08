import psycopg2

def Articles():
    articles = [
        {
            'id': 1,
            'title':'Article One',
            'body':'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            'author':'Brad Traversy',
            'create_date':'04-25-2017'
        },
        {
            'id': 2,
            'title':'Article Two',
            'body':'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            'author':'John Doe',
            'create_date':'04-25-2017'
        },
        {
            'id': 3,
            'title':'Article Three',
            'body':'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            'author':'Brad Traversy',
            'create_date':'04-25-2017'
        }
    ]
    return articles


def buscar_Audio(id):
    conn = psycopg2.connect('postgresql://fezjdtyy:BxOZhSdBMyYrUDpNzs5Rxmh9sW9STTbv@mouse.db.elephantsql.com/fezjdtyy')
    cursor = conn.cursor()
    
    data = []
    cursor.execute(f"""
                     SELECT
                         ca.audio,
                         cq.tipo,
                         ca.idioma
                     FROM
                         campanha_question cq
                     JOIN
                         campanha_audio ca ON cq.questao_id = ca.questao_id
                     WHERE
                         cq.campanha_id = {id};                   
                     """)
    audio_files = [row[0] for row in cursor.fetchall()]


    base_url = "https://insightsap.com/get_audio/"
    audio_urls = [f"{base_url}{audio_file}" for audio_file in audio_files]

    conn.close()

    
    
    return audio_urls


audio = buscar_Audio(19077)

print(audio)