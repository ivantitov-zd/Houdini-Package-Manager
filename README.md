# Houdini Package Manager

Добро пожаловать. Это временный README, который будет заменён на более подробный после выпуска версии 1.0.
На данный момент проект проходит стадию открытого бета тестирования.

## Package Manager является инструментом для:
- Устранения необходимости использовать старый подход к установке через файл .env, а также изучения [нового подхода](https://www.sidefx.com/docs/houdini/ref/plugins.html) или хотя бы отложить это на потом.
- Установки [пакетов](https://www.sidefx.com/docs/houdini/ref/plugins.html) из локальных директорий.
- Установки пакетов, которые размещены авторами на GitHub и подобных веб сервисах (на данный момент доступен только GitHub).
- Просмотра содержимого пакетов (HDA, Shelves и их инструменты).
- Включения и отключения пакетов.
- Обновления пакетов, которые были установлены с веб сервисов.


## Доступ
Доступ ко всем функциям осуществляется через пункт _Packages_ главного меню, который появляется после установки данного менеджера.

![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/main_menu.png)


## Установка локальных пакетов (Main Menu / Packages / Install Local)
Эта функция позволяет установить пакет через указание директории на компьютере, в которую уже распаковано содержимое пакета.

На данный момент установка происходит всего в один этап - создание json файла в "домашней директории Houdini / packages". После перезапуска Houdini пакет будет загружен, но просмотр содержимого в менеджере возможен без перезапуска.

Опция _Setup Schema_ необходима для установки пакетов со сложной структурой, но пока не реализована. В будущем вместе с менеджером будет поставляться некоторое количество заготовленных схем установки для таких пакетов как MOPs и SideFX Labs.

![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/install_local.png)


## Установка пакетов из веба (Main Menu / Packages / Install Web)
Эта функция позволяет установить пакет через указание ссылки на веб репозиторий (пока только GitHub).

Установка происходит в несколько этапов (автоматически):
- Загрузка содержимого
- Распаковка в домашнюю директорию Houdini
- Создание специального файла _package.setup_, который необходим для отслеживания обновлений
- Создание json файла в "домашней директории Houdini / packages".

![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/install_web.png)

#### Из списка
В разделе *Install from Web* основого окна менеджера доступен список репозиториев, которые автор менеджера посчитал достаточно полезными. После ознакомления с информацией, в том числе, перейдя по ссылке в поле *Source*, вы можете установить выбранный пакет в два клика.

![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/manager_install_web.png)
![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/manager_install_web_version.png)


## Просмотр содержимого пакета
В разделе *Installed* основного окна менеджера доступен список всех установленных пакетов, в том числе отключенных, о чем свидетельствует иконка.

На данный момент у пакета можно посмотреть список: HDA; полок; инструментов, которые определены в полках; Python панелей.

На скриншоте ниже пакет Hammer-Tools отключен, но просмотр его содержимого доступен. 

![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/manager_digital_assets.png)

## Управление пакетом
Вкладка _General_ отображает всю доступную информацию о выбранном пакете.

Поле _Source_ и некоторые другие заполнены только в том случае, если известно происхождение пакета (например, GitHub репозиторий).

![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/manager_general.png)

#### Disable
Позволяет отключить текущий пакет. В этом случае при следующем запуске Houdini содержимое пакета загружено не будет.

#### Uninstall
На данный момент кнопка просто удаляет соответствующий json файл из папки packages в домашней директории Houdini. Повторная установка с помощью _Install Local_ обратит этот процесс.

#### Update
Опция _Check on Startup_ указывает на необходимость выполнять проверку на наличие обновлений при запуске Houdini. Данная опция может быть глобально отключена через раздел *Settings* основного окна менеджера.

![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/manager_settings.png)

Опция _Only Stable Releases_ указывает на необходимость проверять доступность только стабильных обновлений (без альфа, бета и подобных версий). Работа данной опции на данный момент полагается на добросовестное указание метки _Pre-release_ авторами.

При каждом запуске Houdini, но не чаще, чем раз в 4 часа, менеджер производит проверку на наличие обновлений для репозиториев, у которых включена опция _Check on Startup_. При условии, что глобальная опция тоже включена. В том случае, если обнаружена новая версия, информация об изменениях будет показана в специальном окне, которое позволяет выбрать только те пакеты, которые вы считаете нужным обновить. Также можно пропустить обновление, но в следующий раз данные обновления снова будут предложены. Опция "пропустить версию" пока не реализована.

![](https://github.com/Houdini-Packages/Houdini-Package-Manager/raw/temp_readme_data/image/updates.png)

## Развитие
Для выпуска версии 1.0 необходимо реализовать систему схем установки и написать подробный help/readme на русском/английском.

О планах на будущие версии можно судить по списку задач в [проекте](https://github.com/Houdini-Packages/Houdini-Package-Manager/projects/1).


## Автор
Иван Титов - [GitHub](https://github.com/ivantitov_zd), [Telegram](http://t.me/ivantitov_zd)
