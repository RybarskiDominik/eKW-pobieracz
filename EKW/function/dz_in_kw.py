from bs4 import BeautifulSoup as BS


def dz_in_kw(id_value=None, page_source=None):

    soup = BS(page_source, 'html.parser')

    elem = soup.findAll('td', separator='')

    my_data = []

    temp = []
    for el in elem:

        if el.text != '':
            if el.text == '\n\n\n\n\n':
                continue
            temp.append(el.text)
        else:
            my_data.append(temp)
            temp = []
            # print('*')

    element = []  # {}
    new_data = {}
    next = False
    last_name = ''
    i = 1

    valid_tags = ["Numer działki", "Identyfikator działki"]
    for md in my_data:
        if 'Numer działki' in md:
            for m in md:
                if next:
                    next = False
                    new_data[last_name] = m.strip()
                if m.strip() in valid_tags:
                    last_name = m
                    next = True
                else:
                    pass

            new_data_with_id = {'id': id_value}
            new_data_with_id.update(new_data)

            element.append(new_data_with_id)

            i += 1
            new_data = {}
    return element


if __name__ == "__main__":
    pass