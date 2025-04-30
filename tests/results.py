"""Test results for validation"""

# ruff: noqa: E501
UUID4 = "c394802542bd4c9990cca50d3104e6a0"

FILE_1_RESULT = {
    "metadata": {
        "Filename": f"{UUID4}_1.pdf",
        "Title": "cmem-plugin-pdfextract_test",
        "Producer": "macOS Version 15.4.1 (Build 24E263) Quartz PDFContext",
        "Author": "eccenca GmbH",
        "Creator": "Word",
        "CreationDate": "D:20250429161555Z00'00'",
        "ModDate": "D:20250429161555Z00'00'",
    },
    "pages": [
        {
            "page_number": 1,
            "text": """Lorem ipsum dolor sit amet. Eum consequatur ipsa aut fugit eligendi non enim rerum
qui quia dolores. Aut nemo mollitia eos porro perferendis ea adipisci soluta aut
delectus eveniet aut ipsum quos non sint inventore aut modi accusantium. Et
perferendis magni ab modi quae non corrupti quam. Eum ipsum expedita aut nulla sunt
ut expedita eaque aut ipsum facilis.
header 1 header 2 header 3 header 4
1/1 2/1 3/1 4/1
1/2 2/2 3/2 4/2
Eum dolorem placeat qui repellendus doloribus ut velit voluptates qui similique esse.
Aut nesciunt totam et magni temporibus sed voluptate atque At repudiandae pariatur ut
neque doloribus et quaerat natus non dolorem fuga. Vel reiciendis velit est rerum
consequatur sed consequuntur nobis aut sequi aliquid et cupiditate dignissimos ut fuga
provident!""",
            "tables": [
                [
                    ["header 1", "header 2", "header 3", "header 4"],
                    ["1/1", "2/1", "3/1", "4/1"],
                    ["1/2", "2/2", "3/2", "4/2"],
                ]
            ],
        },
        {
            "page_number": 2,
            "text": """Qui quidem earum sit saepe galisum non dolor tempore ut tempore dolorem qui itaque
consequuntur et nobis soluta. Aut sint maiores qui velit repudiandae sed veritatis
eligendi ea pariatur quia ea ipsum quia. Id voluptatem velit aut molestiae impedit ut
quaerat repellendus ab dolores illum vel debitis quam et autem quisquam quo nostrum
quam.
header 5 header 6 header 7 header 8
5/1 6/1 7/1 8/1
5/2 6/2 7/2 8/2
Ut Quis nulla non sequi similique et veniam obcaecati sit sapiente possimus ea
tempora temporibus ad voluptas expedita qui facilis fuga. Qui dolor reprehenderit cum
obcaecati dolorem et consequatur architecto et adipisci rerum id reprehenderit eligendi
est porro quam est veritatis sint.""",
            "tables": [
                [
                    ["header 5", "header 6", "header 7", "header 8"],
                    ["5/1", "6/1", "7/1", "8/1"],
                    ["5/2", "6/2", "7/2", "8/2"],
                ]
            ],
        },
    ],
}

FILE_2_RESULT = {
    "metadata": {
        "Filename": f"{UUID4}_2.pdf",
        "Title": "cmem-plugin-pdfextract_test_2",
        "Producer": "macOS Version 15.4.1 (Build 24E263) Quartz PDFContext",
        "Author": "eccenca GmbH",
        "Creator": "Word",
        "CreationDate": "D:20250429161519Z00'00'",
        "ModDate": "D:20250429161519Z00'00'",
    },
    "pages": [
        {
            "page_number": 1,
            "text": """Qui tempore commodi est aspernatur dolor aut laudantium iure. Ut ipsum unde aut
sunt ratione ut sint nobis id quibusdam velit id consequatur voluptatem. Aut corrupti
reiciendis aut laborum velit et modi minima qui praesentium voluptates et repudiandae
omnis rem possimus nobis! Non sint ratione non maiores voluptas aut error distinctio.
header 9 header 10 header 11 header 12
9/1 10/1 11/1 12/1
9/2 10/2 11/2 12/2
Ut repudiandae illo a veritatis quia aut deleniti minus sed eius placeat? Quo earum
voluptatem qui galisum illo non doloremque dignissimos sed earum dolor et nobis
inventore.""",
            "tables": [
                [
                    ["header 9", "header 10", "header 11", "header 12"],
                    ["9/1", "10/1", "11/1", "12/1"],
                    ["9/2", "10/2", "11/2", "12/2"],
                ]
            ],
        },
        {
            "page_number": 2,
            "text": """Ut dolorem galisum est ipsam recusandae in ipsam Quis aut vitae corrupti? Aut minus
perferendis aut sunt animi et magnam dolor. Sed iusto aspernatur cum deleniti dolor ut
totam laudantium hic inventore quasi et dignissimos enim qui commodi quisquam. Est
repellat nobis qui voluptas possimus rem voluptatum quibusdam sed esse nesciunt ut
distinctio libero et sint nihil.
header 13 header 14 header 15 header 16
13/1 14/1 15/1 16/1
13/2 14/2 15/2 16/2
Est libero consectetur ea incidunt corporis sed possimus alias. Est voluptatibus debitis
aut recusandae temporibus rem consequatur optio. Eum quas obcaecati non aperiam
blanditiis aut iusto provident ut recusandae doloremque ex dicta quia qui oIicia
cupiditate ut aliquid praesentium. Est blanditiis totam sed mollitia modi aut amet
omnis et exercitationem modi aut voluptas repellendus non sint sint.""",
            "tables": [
                [
                    ["header 13", "header 14", "header 15", "header 16"],
                    ["13/1", "14/1", "15/1", "16/1"],
                    ["13/2", "14/2", "15/2", "16/2"],
                ]
            ],
        },
    ],
}


FILE_CORRUPTED_RESULT_1 = {
    "metadata": {
        "Filename": "c394802542bd4c9990cca50d3104e6a0_corrupted_1.pdf",
        "error": "No /Root object! - Is this really a PDF?",
    },
    "pages": [],
}


FILE_CORRUPTED_RESULT_2 = {
    "metadata": {"Filename": "c394802542bd4c9990cca50d3104e6a0_corrupted_2.pdf"},
    "pages": [
        {
            "page_number": 1,
            "error": "Text extraction failed or returned None: Data-loss while decompressing "
            "corrupted data",
        }
    ],
}

CUSTOM_TABLE_STRATEGY_SETTING = """
vertical_strategy: lines
horizontal_strategy: lines
intersection_tolerance: 5
snap_tolerance: 3
join_tolerance: 3
edge_min_length: 3
min_words_vertical: 1
min_words_horizontal: 1
"""
