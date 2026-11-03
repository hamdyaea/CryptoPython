# Developer: Hamdy Abou El Anein
# Contact: hamdy.aea@protonmail.com
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from app import add_block, calculate_hash, create_app, initialize


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "chain.db"

    def test_factory_has_no_database_side_effect(self):
        create_app(self.db)
        self.assertFalse(self.db.exists())

    def test_read_and_default_write_denial(self):
        client = create_app(self.db).test_client()
        self.assertEqual(client.get("/blocks").json, [])
        self.assertEqual(client.get("/add_block").status_code, 405)
        self.assertEqual(client.post("/add_block").status_code, 403)
        self.assertEqual(client.get("/blocks").json, [])

    def test_explicit_local_write(self):
        client = create_app(self.db, allow_writes=True).test_client()
        response = client.post("/add_block")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["previous_hash"], "0")
        self.assertEqual(response.json["hash"], calculate_hash(response.json))

    def test_concurrent_appends_form_one_chain(self):
        initialize(self.db)
        with ThreadPoolExecutor(max_workers=4) as pool:
            blocks = list(pool.map(lambda _: add_block(self.db), range(12)))
        blocks.sort(key=lambda block: block["id"])
        self.assertEqual(blocks[0]["previous_hash"], "0")
        for previous, current in zip(blocks, blocks[1:]):
            self.assertEqual(current["previous_hash"], previous["hash"])


if __name__ == "__main__":
    unittest.main()
