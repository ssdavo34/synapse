"""
Wikipedia Service Module

Wikipedia API를 연동하여 검색 및 페이지 내용 조회 기능을 제공합니다.

Features:
    - Wikipedia 페이지 검색 (키워드 기반)
    - 페이지 내용 가져오기 (전체 텍스트 또는 요약)
    - 다국어 지원 (en, ko, ja 등)
    - 메타데이터 포함 (URL, 마지막 수정일 등)

Examples:
    >>> wiki = WikipediaService(language='en')
    >>> results = wiki.search_wikipedia("Python programming", limit=3)
    >>> for result in results:
    ...     print(f"{result['title']}: {result['url']}")
    >>>
    >>> content = wiki.get_page_content("Python (programming language)", sentences=3)
    >>> print(content['summary'])
"""

import re
from typing import List, Dict, Any, Optional
import wikipediaapi
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger

# Logger 설정
logger = setup_logger("WikipediaService")


class WikipediaService:
    """
    Wikipedia API 연동 서비스

    Wikipedia API를 사용하여 페이지 검색, 내용 조회 등의 기능을 제공합니다.
    다국어를 지원하며, 요약본 추출 및 메타데이터 제공이 가능합니다.

    Attributes:
        language (str): Wikipedia 언어 코드 (기본값: 'en')
        user_agent (str): API 요청 시 사용할 User-Agent
        wiki (wikipediaapi.Wikipedia): Wikipedia API 클라이언트
        timeout (int): API 요청 타임아웃 (초)

    Examples:
        >>> # 기본 사용법 (영어)
        >>> wiki = WikipediaService()
        >>> results = wiki.search_wikipedia("Artificial Intelligence")
        >>> print(f"Found {len(results)} results")
        >>>
        >>> # 한국어 사용
        >>> wiki_ko = WikipediaService(language='ko')
        >>> results = wiki_ko.search_wikipedia("인공지능")
        >>> content = wiki_ko.get_page_content(results[0]['title'])
    """

    # 지원 언어 목록
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ko': '한국어',
        'ja': '日本語',
        'zh': '中文',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
    }

    # 기본 User-Agent (Wikipedia API 정책에 따라 필수)
    DEFAULT_USER_AGENT = "SynapseSimple/2.0 (https://github.com/synapse; educational-bot)"

    def __init__(
        self,
        language: str = 'en',
        user_agent: Optional[str] = None,
        timeout: int = 10
    ):
        """
        WikipediaService 초기화

        Args:
            language: Wikipedia 언어 코드 (기본값: 'en')
            user_agent: API 요청 시 사용할 User-Agent. None이면 기본값 사용
            timeout: API 요청 타임아웃 (초, 기본값: 10)

        Raises:
            ValueError: 지원하지 않는 언어 코드인 경우

        Examples:
            >>> # 영어 Wikipedia
            >>> wiki_en = WikipediaService()
            >>>
            >>> # 한국어 Wikipedia
            >>> wiki_ko = WikipediaService(language='ko')
            >>>
            >>> # 커스텀 User-Agent
            >>> wiki = WikipediaService(
            ...     language='en',
            ...     user_agent='MyBot/1.0 (contact@example.com)'
            ... )
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}"
            )

        self.language = language
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT
        self.timeout = timeout

        # Wikipedia API 클라이언트 생성
        self.wiki = wikipediaapi.Wikipedia(
            language=self.language,
            user_agent=self.user_agent,
            timeout=self.timeout
        )

        logger.info(
            "WikipediaService initialized",
            extra={
                "language": self.language,
                "user_agent": self.user_agent,
                "timeout": self.timeout
            }
        )

    def search_wikipedia(
        self,
        query: str,
        limit: int = 3
    ) -> List[Dict[str, str]]:
        """
        Wikipedia 검색

        키워드로 Wikipedia 페이지를 검색하여 상위 N개 결과를 반환합니다.

        Args:
            query: 검색 키워드
            limit: 반환할 최대 결과 수 (기본값: 3)

        Returns:
            검색 결과 리스트. 각 항목은 다음 키를 포함:
            {
                'title': str,  # 페이지 제목
                'url': str,  # 페이지 URL
                'exists': bool  # 페이지 존재 여부
            }

        Examples:
            >>> wiki = WikipediaService()
            >>> results = wiki.search_wikipedia("Python programming", limit=3)
            >>> for result in results:
            ...     print(f"{result['title']}: {result['url']}")
            Python (programming language): https://en.wikipedia.org/...
            Guido van Rossum: https://en.wikipedia.org/...
        """
        logger.info(
            "Starting Wikipedia search",
            extra={
                "query": query,
                "limit": limit,
                "language": self.language
            }
        )

        try:
            # Wikipedia API의 opensearch 사용
            # 참고: wikipediaapi는 직접 검색을 지원하지 않으므로
            # Wikipedia의 opensearch API를 사용해야 합니다
            import requests

            search_url = f"https://{self.language}.wikipedia.org/w/api.php"
            params = {
                'action': 'opensearch',
                'search': query,
                'limit': limit,
                'namespace': 0,
                'format': 'json'
            }

            headers = {
                'User-Agent': self.user_agent
            }

            response = requests.get(
                search_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            # OpenSearch API 응답 형식: [query, [titles], [descriptions], [urls]]
            data = response.json()

            if len(data) < 4:
                logger.warning(
                    "Unexpected search response format",
                    extra={"data": data}
                )
                return []

            titles = data[1]
            urls = data[3]

            results = []
            for title, url in zip(titles, urls):
                # 각 페이지의 존재 여부 확인
                page = self.wiki.page(title)
                results.append({
                    'title': title,
                    'url': url,
                    'exists': page.exists()
                })

            logger.info(
                "Wikipedia search completed",
                extra={
                    "query": query,
                    "results_count": len(results)
                }
            )

            return results

        except requests.exceptions.Timeout:
            logger.error(
                "Wikipedia search timeout",
                extra={
                    "query": query,
                    "timeout": self.timeout
                }
            )
            return []

        except requests.exceptions.RequestException as e:
            logger.error(
                "Wikipedia search failed",
                extra={
                    "query": query,
                    "error": str(e)
                }
            )
            return []

        except Exception as e:
            logger.error(
                "Unexpected error during Wikipedia search",
                extra={
                    "query": query,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return []

    def get_page_content(
        self,
        title: str,
        sentences: int = 3,
        include_full_text: bool = False
    ) -> Dict[str, Any]:
        """
        Wikipedia 페이지 내용 가져오기

        페이지 제목으로 전체 내용을 조회하고, 요약본을 추출합니다.

        Args:
            title: Wikipedia 페이지 제목
            sentences: 요약본에 포함할 문장 수 (기본값: 3)
            include_full_text: 전체 텍스트 포함 여부 (기본값: False)

        Returns:
            페이지 정보 딕셔너리:
            {
                'title': str,  # 페이지 제목
                'url': str,  # 페이지 URL
                'summary': str,  # 요약 (N 문장)
                'full_text': str,  # 전체 텍스트 (include_full_text=True일 때만)
                'exists': bool,  # 페이지 존재 여부
                'language': str,  # 언어 코드
                'categories': List[str],  # 카테고리 목록
                'links_count': int,  # 링크 개수
                'error': str  # 에러 메시지 (존재하지 않는 페이지 등)
            }

        Examples:
            >>> wiki = WikipediaService()
            >>> content = wiki.get_page_content(
            ...     "Python (programming language)",
            ...     sentences=3
            ... )
            >>> print(content['summary'])
            Python is a high-level, general-purpose programming language...
        """
        logger.info(
            "Fetching Wikipedia page content",
            extra={
                "title": title,
                "sentences": sentences,
                "language": self.language
            }
        )

        try:
            # 페이지 가져오기
            page = self.wiki.page(title)

            # 페이지가 존재하지 않는 경우
            if not page.exists():
                logger.warning(
                    "Wikipedia page not found",
                    extra={"title": title}
                )
                return {
                    'title': title,
                    'url': '',
                    'summary': '',
                    'full_text': '',
                    'exists': False,
                    'language': self.language,
                    'categories': [],
                    'links_count': 0,
                    'error': f"Page '{title}' does not exist"
                }

            # 요약본 추출
            summary = self._extract_summary(page.text, sentences)

            # 카테고리 추출
            categories = list(page.categories.keys())

            # 결과 딕셔너리 구성
            result = {
                'title': page.title,
                'url': page.fullurl,
                'summary': summary,
                'exists': True,
                'language': self.language,
                'categories': categories[:5],  # 상위 5개 카테고리만
                'links_count': len(page.links)
            }

            # 전체 텍스트 포함 옵션
            if include_full_text:
                result['full_text'] = page.text

            logger.info(
                "Wikipedia page content fetched successfully",
                extra={
                    "title": page.title,
                    "summary_length": len(summary),
                    "full_text_length": len(page.text),
                    "categories_count": len(categories),
                    "links_count": result['links_count']
                }
            )

            return result

        except Exception as e:
            logger.error(
                "Failed to fetch Wikipedia page content",
                extra={
                    "title": title,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return {
                'title': title,
                'url': '',
                'summary': '',
                'full_text': '',
                'exists': False,
                'language': self.language,
                'categories': [],
                'links_count': 0,
                'error': f"Error fetching page: {str(e)}"
            }

    def _extract_summary(self, text: str, sentences: int) -> str:
        """
        텍스트에서 요약본 추출

        전체 텍스트에서 첫 N개 문장을 추출하여 요약본을 만듭니다.
        문장은 마침표(.), 느낌표(!), 물음표(?)로 구분합니다.

        Args:
            text: 전체 텍스트
            sentences: 추출할 문장 수

        Returns:
            요약 텍스트 (N개 문장)

        Examples:
            >>> wiki = WikipediaService()
            >>> text = "First sentence. Second sentence. Third sentence."
            >>> summary = wiki._extract_summary(text, 2)
            >>> print(summary)
            First sentence. Second sentence.
        """
        if not text:
            return ""

        # 문장 분리 정규식
        # 마침표, 느낌표, 물음표 뒤에 공백이 오는 경우를 문장 끝으로 인식
        # 단, 약어(Mr., Dr. 등)는 제외
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'

        # 문장 분리
        all_sentences = re.split(sentence_pattern, text)

        # 빈 문장 제거
        all_sentences = [s.strip() for s in all_sentences if s.strip()]

        # 요청한 문장 수만큼 추출
        selected_sentences = all_sentences[:sentences]

        # 문장 결합
        summary = ' '.join(selected_sentences)

        logger.debug(
            "Summary extracted",
            extra={
                "total_sentences": len(all_sentences),
                "extracted_sentences": len(selected_sentences),
                "summary_length": len(summary)
            }
        )

        return summary

    def get_page_summary_with_metadata(self, title: str) -> Dict[str, Any]:
        """
        페이지 요약과 메타데이터를 함께 가져오기

        페이지의 기본 요약(summary 속성)과 추가 메타데이터를 반환합니다.
        이 메서드는 Wikipedia API의 summary 속성을 직접 사용합니다.

        Args:
            title: Wikipedia 페이지 제목

        Returns:
            페이지 요약 및 메타데이터:
            {
                'title': str,
                'url': str,
                'summary': str,  # Wikipedia의 기본 요약
                'exists': bool,
                'language': str
            }

        Examples:
            >>> wiki = WikipediaService()
            >>> info = wiki.get_page_summary_with_metadata("Python")
            >>> print(info['summary'])
        """
        logger.info(
            "Fetching Wikipedia page summary",
            extra={"title": title}
        )

        try:
            page = self.wiki.page(title)

            if not page.exists():
                logger.warning(
                    "Wikipedia page not found",
                    extra={"title": title}
                )
                return {
                    'title': title,
                    'url': '',
                    'summary': '',
                    'exists': False,
                    'language': self.language,
                    'error': f"Page '{title}' does not exist"
                }

            result = {
                'title': page.title,
                'url': page.fullurl,
                'summary': page.summary,
                'exists': True,
                'language': self.language
            }

            logger.info(
                "Wikipedia page summary fetched",
                extra={
                    "title": page.title,
                    "summary_length": len(page.summary)
                }
            )

            return result

        except Exception as e:
            logger.error(
                "Failed to fetch Wikipedia page summary",
                extra={
                    "title": title,
                    "error": str(e)
                }
            )
            return {
                'title': title,
                'url': '',
                'summary': '',
                'exists': False,
                'language': self.language,
                'error': f"Error: {str(e)}"
            }


# 테스트 코드
if __name__ == "__main__":
    print("=== Wikipedia Service Test ===\n")

    # 1. 영어 Wikipedia 서비스 생성
    print("🔄 Test 1: Initialize WikipediaService (English)")
    wiki_en = WikipediaService(language='en')
    print(f"✅ English Wikipedia service initialized\n")

    # 2. 검색 테스트
    print("🔄 Test 2: Search 'Python programming'")
    search_results = wiki_en.search_wikipedia("Python programming", limit=3)
    print(f"✅ Found {len(search_results)} results:")
    for i, result in enumerate(search_results, 1):
        print(f"   {i}. {result['title']}")
        print(f"      URL: {result['url']}")
        print(f"      Exists: {result['exists']}")
    print()

    # 3. 페이지 내용 가져오기 (요약본)
    if search_results:
        first_title = search_results[0]['title']
        print(f"🔄 Test 3: Get page content for '{first_title}'")
        content = wiki_en.get_page_content(first_title, sentences=3)

        if content['exists']:
            print(f"✅ Page content fetched successfully")
            print(f"   Title: {content['title']}")
            print(f"   URL: {content['url']}")
            print(f"   Categories: {', '.join(content['categories'][:3])}")
            print(f"   Links count: {content['links_count']}")
            print(f"   Summary preview: {content['summary'][:200]}...")
        else:
            print(f"❌ Page not found: {content.get('error')}")
        print()

    # 4. 존재하지 않는 페이지 테스트
    print("🔄 Test 4: Non-existent page")
    nonexistent = wiki_en.get_page_content("ThisPageDoesNotExist12345")
    if not nonexistent['exists']:
        print(f"✅ Non-existent page correctly handled")
        print(f"   Error: {nonexistent.get('error')}")
    else:
        print(f"❌ Should return exists=False")
    print()

    # 5. 한국어 Wikipedia 테스트
    print("🔄 Test 5: Korean Wikipedia - Search '인공지능'")
    wiki_ko = WikipediaService(language='ko')
    ko_results = wiki_ko.search_wikipedia("인공지능", limit=3)
    print(f"✅ Found {len(ko_results)} Korean results:")
    for i, result in enumerate(ko_results, 1):
        print(f"   {i}. {result['title']}")
    print()

    # 6. 한국어 페이지 내용
    if ko_results:
        print(f"🔄 Test 6: Get Korean page content")
        ko_content = wiki_ko.get_page_content(ko_results[0]['title'], sentences=2)
        if ko_content['exists']:
            print(f"✅ Korean page content fetched")
            print(f"   Title: {ko_content['title']}")
            print(f"   Summary: {ko_content['summary'][:150]}...")
        print()

    # 7. 페이지 요약 메타데이터 테스트
    print("🔄 Test 7: Get page summary with metadata")
    summary_info = wiki_en.get_page_summary_with_metadata("Artificial Intelligence")
    if summary_info['exists']:
        print(f"✅ Summary fetched successfully")
        print(f"   Title: {summary_info['title']}")
        print(f"   Summary length: {len(summary_info['summary'])} chars")
        print(f"   Preview: {summary_info['summary'][:150]}...")
    else:
        print(f"❌ Failed to fetch summary: {summary_info.get('error')}")
    print()

    print("=== All tests completed ===")
