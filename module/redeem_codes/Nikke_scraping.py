from time import sleep
from typing import List

import bs4
import requests


class GetCodes:
    BASE_URL: str = "https://nikke.gg/cd-keys-guide/"

    # GAME_CODES: dict = {
    #     "genshin": "genshin-impact",
    #     "hkrpg": "honkai-star-rail"
    # }

    def get_codes(self) -> List[str]:
        url = self._build_url()
        response = self._send_request(url)
        soup = self._parse_html(response)
        # print(soup)
        # soup = bs4.BeautifulSoup(response, "html.parser")
        parsed_codes = self._extract_codes(soup)
        return parsed_codes

    def _check_codes(self, codes: List[str], game: str = "genshin") -> List[str]:
        file = f"files/redeemed_codes_NIKKE.txt"
        with open(file, "r") as f:
            codes_redeemed = f.read().splitlines()
        return [x for x in codes if x not in codes_redeemed]

    # async def redeem_codes(self, client: genshin.Client, codes: List[str], game: genshin.Game = "genshin") -> None:
    #     active_codes = self._check_codes(codes, game)
    #     file = f"files/redeemed_codes_{game}.txt"
    #     for code in active_codes:
    #         try:
    #             await client.redeem_code(code, game=game)
    #         except (genshin.RedemptionClaimed, genshin.RedemptionInvalid,
    #                 genshin.RedemptionException, genshin.InvalidCookies):
    #             pass
    #         finally:
    #             with open(file, "a") as f:
    #                 f.write(f"{code}\n")
    #         sleep(6)

    def _build_url(self) -> str:
        # game_slug = self.GAME_CODES.get(game, "")
        # if not game_slug:
            # raise Exception(f"Game {game} is not supported")
        return f"{self.BASE_URL}"

    def _send_request(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def _parse_html(self, html: str) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(html, "html.parser")
        return soup.find("figure", {"class": "wp-block-table"})

    def _extract_codes(self, soup: bs4.BeautifulSoup) -> List[bs4.element.Tag]:
        # Find all <mark> tags within <td> tags
        mark_tags = soup.find_all('mark')

        # Extract text from <mark> tags
        codes = [mark_tag.text.strip() for mark_tag in mark_tags]

        # Print the result
        return codes
    
    
import aiohttp
import asyncio
from typing import List

class CustomRedeemer:
    async def redeem_codes(self, codes: List[str]) -> None:
        file = "files/redeemed_codes_nikke.txt"
        for code in codes:
            try:
                await self.redeem_code(code)
            except Exception as e:
                print(f"Error redeeming code {code}: {e}")
            finally:
                with open(file, "a") as f:
                    f.write(f"{code}\n")
                await asyncio.sleep(6)

    
if __name__ == "__main__":
    a = GetCodes()
    codes = a.get_codes()
    print(a._check_codes(codes))