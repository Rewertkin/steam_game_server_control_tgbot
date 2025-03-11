Бот для управления собственным STEAM сервером через телеграмм бот. 
В настоящий момент протестирован для управления выделенными серверами Valheim и Icarus.

**Поддерживаемые функции:** 
1. Ручной запуск сервера;
2. Ручное обновление сервера;
3. Ручная остановка сервера
4. Статус сервера - выводится текущее состояние сервера. 
5. Автоматическое обновление сервера.

**Для запуска требуется:** 
В .env файле: 
	API_TOKEN= указываем TG токкен бота
	STEAMAPI= указываем STEAM API ключ

В config.json файле:
	"allowed_users"  = указывается список id TG пользователей, кто может пользоваться ботом, остальным выводится ошибка при заходе в бот
	"app_id" = указывается идентификатор игры согласно https://steamdb.info/  для Valheim это - 892970
	"start_server" = указывается путь до исполняемого файла для запуска сервера
	"stop_server" = указывается путь до исполняемого файла для остановки сервера
	"update_server" = указывается путь до исполняемого файла для обновления сервера
	"start_waiting_time" = время ожидания запуска сервера
	"bg_waiting_time" = указывается время, с какой периодичностью сервер будет проверять обновления для игры
	"stop_waiting_time" = время ожидания приостановки сервера
	"addr" = адрес игрового сервера
	"game_version" = заполняется автоматически, после обновления игрового сервера
