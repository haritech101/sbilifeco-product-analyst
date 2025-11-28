from asyncio import run, sleep
from dotenv import load_dotenv
from os import getenv
from sbilifeco.gateways.readers.pdf.docling_reader import DoclingReader
from sbilifeco.cp.material_reader.http_server import MaterialReaderHttpServer
from envvars import EnvVars, Defaults


class DoclingReaderMicroservice:
    async def run(self) -> None:
        # Env vars
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        doclingserve_proto = getenv(
            EnvVars.doclingserve_proto, Defaults.doclingserve_proto
        )
        doclingserve_host = getenv(
            EnvVars.doclingserve_host, Defaults.doclingserve_host
        )
        doclingserve_port = int(
            getenv(EnvVars.doclingserve_port, Defaults.doclingserve_port)
        )

        # Gateways
        self.reader = (
            DoclingReader()
            .set_doclingserve_proto(doclingserve_proto)
            .set_doclingserve_host(doclingserve_host)
            .set_doclingserve_port(doclingserve_port)
        )

        # Controllers and presenters
        self.http_server = MaterialReaderHttpServer()
        self.http_server.set_material_reader(self.reader).set_http_port(http_port)
        await self.http_server.listen()

    async def run_forever(self) -> None:
        await self.run()
        while True:
            await sleep(5000)


if __name__ == "__main__":
    load_dotenv()
    run(DoclingReaderMicroservice().run_forever())
