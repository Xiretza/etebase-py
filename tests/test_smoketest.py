import unittest
from etebase import Client, Account, FetchOptions


STORED_SESSION = "gqd2ZXJzaW9uAa1lbmNyeXB0ZWREYXRhxQGr_KWyDChQ6tXOJwJKf0Kw3QyR99itPIF3vZ5w6pVXSIq7AWul3fIXjIZOsBEwTVRumw7e9Af38D5oIL2VLNPLlmTOMjzIvuB00z3zDMFbH8pwrg2p_FvAhLHGjUGoXzU2XIxS4If7rQUfEz1zWkHPqWMrj4hACML5fks302dOUw7OsSMekcQaaVqMyj82MY3lG2qj8CL6ykSED7nW6OYWwMBJ1rSDGXhQRd5JuCGl6kgAHxKS6gkkIAWeUKjC6-Th2etk1XPKDiks0SZrQpmuXG8h_TBdd4igjRUqnIk09z5wvJFViXIU4M3pQomyFPk3Slh7KHvWhzxG0zbC2kUngQZ5h-LbVTLuT_TQWjYmHiOIihenrzl7z9MLebUq6vuwusZMRJ1Atau0Y2HcOzulYt4tLRP49d56qFEId3R4xomZ666hy-EFodsbzpxEKHeBUro3_gifOOKR8zkyLKTRz1UipZfKvnWk_RHFgZlSClRsXyaP34wstUavSiz-HNmTEmflNQKM7Awfel108FcSbW9NQAogW2Y2copP-P-R-DiHThrXmgDsWkTQFA"
SERVER_URL = "http://localhost:3735"
COL_TYPE = "some.coltype"

class TestStringMethods(unittest.TestCase):
    def test_main(self):
        client = Client("python_test", SERVER_URL)

        self.assertTrue(Account.is_etebase_server(client))

        etebase = Account.restore(client, STORED_SESSION, None)
        etebase.force_server_url(SERVER_URL)
        etebase.fetch_token()

        col_mgr = etebase.get_collection_manager()
        col_meta = {"name": "Name"}
        col = col_mgr.create(COL_TYPE, col_meta, b"Something")
        col_meta["bloop"] = "blap"
        col.meta = col_meta
        self.assertEqual(b"Something", bytes(col.content))
        self.assertEqual(COL_TYPE, col.collection_type)

        fetch_options = FetchOptions().prefetch(True)
        col_mgr.upload(col, fetch_options)

        col_list = col_mgr.list(COL_TYPE, None)
        self.assertNotEqual(0, len(list(col_list.data)))
        fetch_options = FetchOptions().stoken(col_list.stoken)
        col_list = col_mgr.list(COL_TYPE, fetch_options)
        self.assertEqual(0, len(list(col_list.data)))

        col2 = col_mgr.fetch(col.uid, None)
        self.assertEqual(b"Something", bytes(col2.content))
        col2.content = b"Something else"
        col_mgr.transaction(col2, None)

        it_mgr = col_mgr.get_item_manager(col)
        item_meta = {"type": "Bla"}
        item = it_mgr.create(item_meta, b"Something item")
        item_meta = {"type": "Bla", "bloop": "blap"}
        item.meta = item_meta
        self.assertNotEqual("", item.uid)
        self.assertIsNotNone(item.etag)
        self.assertEqual(b"Something item", bytes(item.content))

        it_mgr.batch([item], None, None)
        etag1 = item.etag
        self.assertIsNotNone(etag1)
        item.content = b"Something item2"

        it_mgr.transaction([item], None, None)
        self.assertNotEqual(item.etag, etag1)

        item_list = it_mgr.list(None)
        self.assertEqual(1, len(list(item_list.data)))
        it_first = list(item_list.data)[0]
        self.assertEqual(b"Something item2", bytes(it_first.content))

        fetch_options = FetchOptions().stoken(item_list.stoken)
        item_list = it_mgr.list(fetch_options)
        self.assertEqual(0, len(list(item_list.data)))

        etebase.logout()
