from configparser import ConfigParser


def config_db(filename="database.ini", section="postgresql"):
    parser = ConfigParser()

    with open(filename, "r") as config_file:
        parser.read_file(config_file)

    if parser.has_section(section):
        database = {param[0]: param[1] for param in parser.items(section)}
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return database
