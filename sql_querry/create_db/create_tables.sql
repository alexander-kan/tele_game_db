CREATE TABLE IF NOT EXISTS platform_dictionary ( --Таблица со справочником платформ
    platform_dictionary_id integer PRIMARY KEY AUTOINCREMENT, --Идентификатор записи справочника платформ
    platform_name text NOT NULL --Имя платформы
    );
CREATE TABLE IF NOT EXISTS status_dictionary ( --Таблица со справочником статусов прохождения
    status_dictionary_id integer PRIMARY KEY AUTOINCREMENT, --Идентификатор записи справочника статусов
    status_name text NOT NULL --Имя статуса
    );
CREATE TABLE IF NOT EXISTS games ( --общая таблица с играми
    game_id text PRIMARY KEY, --Идентификатор будет создаваться GUID
    game_name text NOT NULL, --Имя игры, официальное, полное
    status integer NOT NULL, --Текущий статус игры
    release_date date NOT NULL, --Дата выпуска игры
    press_score float NOT NULL, --Оценка прессы
    user_score float NOT NULL, --Оценка игроков
    my_score integer, --Моя оценка
    metacritic_url text NOT NULL, --Ссылка на метакритик
    trailer_url text NOT NULL, --Ссылка на трайлер
    average_time_beat float NOT NULL, --Среднее время прохождения
    my_time_beat float, --Моё время прохождения
    last_launch_date date, --Дата последнего запуска игры
    FOREIGN KEY (status) REFERENCES status_dictionary (status_dictionary_id)
    );
CREATE TABLE IF NOT EXISTS games_on_platforms ( --на каких платформах у меня есть игра
    games_on_platform_id integer PRIMARY KEY AUTOINCREMENT, --Идентификатор записи игры на платформе
    platform_id integer NOT NULL, --Наименование платформы
    reference_game_id text NOT NULL, --Связь с игрой
    FOREIGN KEY (reference_game_id) REFERENCES games (game_id),
    FOREIGN KEY (platform_id) REFERENCES platform_dictionary (platform_dictionary_id)
    );
CREATE TABLE IF NOT EXISTS beat_on_platforms ( --на каких платформах я эту игру прошёл и сколько раз
    beat_on_platform_id integer PRIMARY KEY AUTOINCREMENT, --Идентификатор записи платформы на которой пройдена игра
    platform_id integer NOT NULL, --Наименование платформы
    game_id text NOT NULL, --Связь с игрой
    number_of_beat integer, --Сколько раз я её проходил
    FOREIGN KEY (game_id) REFERENCES games (game_id),
    FOREIGN KEY (platform_id) REFERENCES platform_dictionary (platform_dictionary_id)
    );
