"""Test results for validation"""

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
            "text": "Lorem ipsum dolor sit amet. Eum consequatur ipsa aut fugit eligendi non enim rerum\nqui quia dolores. Aut nemo mollitia eos porro perferendis ea adipisci soluta aut\ndelectus eveniet aut ipsum quos non sint inventore aut modi accusantium. Et\nperferendis magni ab modi quae non corrupti quam. Eum ipsum expedita aut nulla sunt\nut expedita eaque aut ipsum facilis.\nheader 1 header 2 header 3 header 4\n1/1 2/1 3/1 4/1\n1/2 2/2 3/2 4/2\nEum dolorem placeat qui repellendus doloribus ut velit voluptates qui similique esse.\nAut nesciunt totam et magni temporibus sed voluptate atque At repudiandae pariatur ut\nneque doloribus et quaerat natus non dolorem fuga. Vel reiciendis velit est rerum\nconsequatur sed consequuntur nobis aut sequi aliquid et cupiditate dignissimos ut fuga\nprovident!",
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
            "text": "Qui quidem earum sit saepe galisum non dolor tempore ut tempore dolorem qui itaque\nconsequuntur et nobis soluta. Aut sint maiores qui velit repudiandae sed veritatis\neligendi ea pariatur quia ea ipsum quia. Id voluptatem velit aut molestiae impedit ut\nquaerat repellendus ab dolores illum vel debitis quam et autem quisquam quo nostrum\nquam.\nheader 5 header 6 header 7 header 8\n5/1 6/1 7/1 8/1\n5/2 6/2 7/2 8/2\nUt Quis nulla non sequi similique et veniam obcaecati sit sapiente possimus ea\ntempora temporibus ad voluptas expedita qui facilis fuga. Qui dolor reprehenderit cum\nobcaecati dolorem et consequatur architecto et adipisci rerum id reprehenderit eligendi\nest porro quam est veritatis sint.",
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
            "text": "Qui tempore commodi est aspernatur dolor aut laudantium iure. Ut ipsum unde aut\nsunt ratione ut sint nobis id quibusdam velit id consequatur voluptatem. Aut corrupti\nreiciendis aut laborum velit et modi minima qui praesentium voluptates et repudiandae\nomnis rem possimus nobis! Non sint ratione non maiores voluptas aut error distinctio.\nheader 9 header 10 header 11 header 12\n9/1 10/1 11/1 12/1\n9/2 10/2 11/2 12/2\nUt repudiandae illo a veritatis quia aut deleniti minus sed eius placeat? Quo earum\nvoluptatem qui galisum illo non doloremque dignissimos sed earum dolor et nobis\ninventore.",
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
            "text": "Ut dolorem galisum est ipsam recusandae in ipsam Quis aut vitae corrupti? Aut minus\nperferendis aut sunt animi et magnam dolor. Sed iusto aspernatur cum deleniti dolor ut\ntotam laudantium hic inventore quasi et dignissimos enim qui commodi quisquam. Est\nrepellat nobis qui voluptas possimus rem voluptatum quibusdam sed esse nesciunt ut\ndistinctio libero et sint nihil.\nheader 13 header 14 header 15 header 16\n13/1 14/1 15/1 16/1\n13/2 14/2 15/2 16/2\nEst libero consectetur ea incidunt corporis sed possimus alias. Est voluptatibus debitis\naut recusandae temporibus rem consequatur optio. Eum quas obcaecati non aperiam\nblanditiis aut iusto provident ut recusandae doloremque ex dicta quia qui oIicia\ncupiditate ut aliquid praesentium. Est blanditiis totam sed mollitia modi aut amet\nomnis et exercitationem modi aut voluptas repellendus non sint sint.",
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
