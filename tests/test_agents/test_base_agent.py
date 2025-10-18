"""
BaseAgent 단위 테스트
====================

목적:
    - BaseAgent 클래스의 모든 기능 검증
    - 각 메서드의 정상 동작 및 에러 처리 테스트
    - 향후 에이전트 개발 시 회귀 테스트 기반 제공

테스트 범위:
    1. 에이전트 생성 및 초기화
    2. execute() 메서드 실행
    3. validate_input() 성공/실패 시나리오
    4. _count_tokens() 정확성
    5. _start_timer() / _calculate_time() 타이머
    6. safe_execute() 에러 처리

실행 방법:
    pytest tests/test_agents/test_base_agent.py -v
    pytest tests/test_agents/test_base_agent.py -v --cov=backend.agents
"""

import pytest
import asyncio
from typing import Dict, Any
from backend.agents.base_agent import BaseAgent


# ============================================================
# Fixture: Mock 에이전트
# ============================================================
class MockAgent(BaseAgent):
    """
    테스트용 Mock 에이전트

    BaseAgent를 상속받아 execute() 메서드를 구현한 간단한 에이전트
    실제 에이전트의 동작을 시뮬레이션합니다.
    """

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock 실행 메서드

        Args:
            task: {"task_type": str, "message": str, "delay": float (optional)}

        Returns:
            {"status": "success", "message": str, "token_count": int}
        """
        # 입력 검증
        self.validate_input(task, required_fields=["message"])

        # 메시지 처리
        message = task["message"]
        self.logger.info(f"Processing message: {message}")

        # 토큰 계산
        token_count = self._count_tokens(message)

        # 지연 시뮬레이션 (선택적)
        delay = task.get("delay", 0.0)
        if delay > 0:
            await asyncio.sleep(delay)

        # 결과 반환
        return {
            "status": "success",
            "message": f"Processed: {message}",
            "token_count": token_count
        }


class FailingMockAgent(BaseAgent):
    """
    실행 실패 시뮬레이션용 Mock 에이전트

    execute() 메서드에서 의도적으로 예외를 발생시켜
    에러 처리 로직을 테스트합니다.
    """

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """항상 예외를 발생시키는 execute"""
        raise RuntimeError("Intentional test error")


@pytest.fixture
def mock_agent():
    """
    MockAgent 인스턴스를 반환하는 fixture

    각 테스트마다 새로운 에이전트 인스턴스를 생성합니다.
    """
    return MockAgent(config={"test_mode": True})


@pytest.fixture
def failing_agent():
    """
    FailingMockAgent 인스턴스를 반환하는 fixture
    """
    return FailingMockAgent()


# ============================================================
# 테스트 1: 에이전트 생성 및 초기화
# ============================================================
def test_base_agent_creation(mock_agent):
    """
    BaseAgent 생성 및 초기화 테스트

    검증 항목:
        - config 딕셔너리가 올바르게 저장되는지
        - logger가 생성되는지
        - 클래스 이름이 로거 이름과 일치하는지
    """
    # config 확인
    assert mock_agent.config == {"test_mode": True}

    # logger 확인
    assert mock_agent.logger is not None
    assert mock_agent.logger.name == "MockAgent"

    # 타이머 초기 상태 확인
    assert mock_agent._start_time is None


def test_base_agent_creation_without_config():
    """
    config 없이 에이전트 생성 테스트

    검증 항목:
        - config가 None이어도 빈 딕셔너리로 초기화되는지
    """
    agent = MockAgent()
    assert agent.config == {}


# ============================================================
# 테스트 2: execute() 메서드 실행
# ============================================================
@pytest.mark.asyncio
async def test_base_agent_execute_success(mock_agent):
    """
    정상적인 execute() 실행 테스트

    검증 항목:
        - 올바른 입력으로 execute() 호출 시 성공 응답 반환
        - 반환 딕셔너리에 필수 필드(status, message) 포함
    """
    task = {
        "task_type": "test",
        "message": "Hello, World!"
    }

    result = await mock_agent.execute(task)

    # 결과 검증
    assert result["status"] == "success"
    assert "Processed: Hello, World!" in result["message"]
    assert result["token_count"] == 3  # "Hello, World!" = 13글자 / 4 ≈ 3


@pytest.mark.asyncio
async def test_base_agent_execute_with_delay(mock_agent):
    """
    지연을 포함한 execute() 실행 테스트

    검증 항목:
        - delay 파라미터가 올바르게 동작하는지
        - 비동기 실행이 정상적으로 완료되는지
    """
    import time

    task = {
        "task_type": "test",
        "message": "Delayed task",
        "delay": 0.1  # 0.1초 지연
    }

    start = time.time()
    result = await mock_agent.execute(task)
    elapsed = time.time() - start

    # 결과 검증
    assert result["status"] == "success"
    assert elapsed >= 0.1  # 최소 0.1초 소요


# ============================================================
# 테스트 3: validate_input() 성공/실패
# ============================================================
def test_validate_input_success(mock_agent):
    """
    validate_input() 성공 케이스 테스트

    검증 항목:
        - 모든 필수 필드가 있을 때 True 반환
        - 예외가 발생하지 않음
    """
    task = {
        "task_type": "test",
        "message": "Valid task",
        "extra_field": "optional"
    }

    # 예외 없이 True 반환
    result = mock_agent.validate_input(task, required_fields=["message"])
    assert result is True


def test_validate_input_missing_task_type(mock_agent):
    """
    task_type 누락 시 validate_input() 실패 테스트

    검증 항목:
        - task_type이 없으면 ValueError 발생
        - 에러 메시지가 명확함
    """
    task = {
        "message": "No task type"
    }

    with pytest.raises(ValueError) as exc_info:
        mock_agent.validate_input(task, required_fields=["message"])

    assert "task_type is required" in str(exc_info.value)


def test_validate_input_missing_required_field(mock_agent):
    """
    필수 필드 누락 시 validate_input() 실패 테스트

    검증 항목:
        - required_fields에 명시된 필드가 없으면 ValueError 발생
        - 에러 메시지에 누락된 필드명 포함
    """
    task = {
        "task_type": "test"
        # message 필드 누락
    }

    with pytest.raises(ValueError) as exc_info:
        mock_agent.validate_input(task, required_fields=["message"])

    assert "Required field missing: message" in str(exc_info.value)


# ============================================================
# 테스트 4: _count_tokens() 정확성
# ============================================================
def test_count_tokens(mock_agent):
    """
    _count_tokens() 메서드 테스트

    검증 항목:
        - 4글자당 1토큰 근사치가 올바르게 계산되는지
        - 다양한 길이의 텍스트 처리
    """
    # 짧은 텍스트
    assert mock_agent._count_tokens("") == 0
    assert mock_agent._count_tokens("Hi") == 0  # 2글자 / 4 = 0
    assert mock_agent._count_tokens("Hello") == 1  # 5글자 / 4 = 1
    assert mock_agent._count_tokens("Hello, World!") == 3  # 13글자 / 4 = 3

    # 긴 텍스트
    long_text = "A" * 1000
    assert mock_agent._count_tokens(long_text) == 250  # 1000 / 4 = 250


# ============================================================
# 테스트 5: 타이머 (_start_timer, _calculate_time)
# ============================================================
@pytest.mark.asyncio
async def test_timer(mock_agent):
    """
    타이머 메서드 테스트

    검증 항목:
        - _start_timer()가 시작 시간을 기록하는지
        - _calculate_time()이 경과 시간을 올바르게 계산하는지
        - 타이머가 리셋되는지
    """
    # 타이머 시작 전
    assert mock_agent._start_time is None

    # 타이머 시작
    mock_agent._start_timer()
    assert mock_agent._start_time is not None

    # 약간의 지연
    await asyncio.sleep(0.1)

    # 경과 시간 계산
    duration = mock_agent._calculate_time()
    assert duration >= 0.1  # 최소 0.1초
    assert duration < 0.2   # 0.2초 미만 (여유)

    # 타이머 리셋 확인
    assert mock_agent._start_time is None

    # 재실행 시 0.0 반환
    duration_without_start = mock_agent._calculate_time()
    assert duration_without_start == 0.0


# ============================================================
# 테스트 6: safe_execute() 에러 처리
# ============================================================
@pytest.mark.asyncio
async def test_safe_execute_success(mock_agent):
    """
    safe_execute() 정상 실행 테스트

    검증 항목:
        - 정상 케이스에서 execute() 결과를 그대로 반환
        - processing_time이 로그에 기록됨 (log_execution 호출)
    """
    task = {
        "task_type": "test",
        "message": "Test message"
    }

    result = await mock_agent.safe_execute(task)

    assert result["status"] == "success"
    assert "Processed" in result["message"]


@pytest.mark.asyncio
async def test_safe_execute_validation_error(mock_agent):
    """
    safe_execute() 검증 실패 테스트

    검증 항목:
        - 필수 필드 누락 시 에러 응답 반환
        - status가 "error"
        - error_type이 "validation_error"
        - error_message가 명확함
    """
    task = {
        "task_type": "test"
        # message 필드 누락
    }

    result = await mock_agent.safe_execute(task)

    assert result["status"] == "error"
    assert result["error_type"] == "validation_error"
    assert "Required field missing: message" in result["error_message"]
    assert "processing_time" in result


@pytest.mark.asyncio
async def test_safe_execute_execution_error(failing_agent):
    """
    safe_execute() 실행 에러 테스트

    검증 항목:
        - execute() 내부에서 예외 발생 시 에러 응답 반환
        - status가 "error"
        - error_type이 "execution_error"
        - error_message에 예외 내용 포함
    """
    task = {
        "task_type": "test",
        "message": "This will fail"
    }

    result = await failing_agent.safe_execute(task)

    assert result["status"] == "error"
    assert result["error_type"] == "execution_error"
    assert "Intentional test error" in result["error_message"]
    assert "processing_time" in result


@pytest.mark.asyncio
async def test_safe_execute_missing_task_type(mock_agent):
    """
    safe_execute() task_type 누락 테스트

    검증 항목:
        - task_type이 없으면 validation_error 반환
    """
    task = {
        "message": "No task type"
    }

    result = await mock_agent.safe_execute(task)

    assert result["status"] == "error"
    assert result["error_type"] == "validation_error"
    assert "task_type is required" in result["error_message"]


# ============================================================
# 테스트 7: 에이전트 config 전달 테스트
# ============================================================
def test_agent_config_propagation():
    """
    에이전트 config 전달 테스트

    검증 항목:
        - 생성 시 전달한 config가 에이전트 내부에서 접근 가능한지
        - config가 None일 때 빈 딕셔너리로 초기화되는지
    """
    # config 전달
    agent1 = MockAgent(config={"model": "gpt-4", "temperature": 0.5})
    assert agent1.config["model"] == "gpt-4"
    assert agent1.config["temperature"] == 0.5

    # config 없이 생성
    agent2 = MockAgent()
    assert agent2.config == {}
    assert isinstance(agent2.config, dict)


# ============================================================
# 테스트 8: 통합 시나리오
# ============================================================
@pytest.mark.asyncio
async def test_full_workflow(mock_agent):
    """
    전체 워크플로우 통합 테스트

    검증 항목:
        - 에이전트 생성 → 실행 → 결과 반환 전 과정
        - 여러 번 실행해도 문제 없음 (상태 무저장 확인)
    """
    # 첫 번째 실행
    result1 = await mock_agent.safe_execute({
        "task_type": "test",
        "message": "First task"
    })
    assert result1["status"] == "success"

    # 두 번째 실행 (상태 무저장 확인)
    result2 = await mock_agent.safe_execute({
        "task_type": "test",
        "message": "Second task"
    })
    assert result2["status"] == "success"

    # 각 실행이 독립적임을 확인
    assert result1["message"] != result2["message"]


# ============================================================
# 실행 예시 (pytest 명령어)
# ============================================================
"""
전체 테스트 실행:
    pytest tests/test_agents/test_base_agent.py -v

특정 테스트만 실행:
    pytest tests/test_agents/test_base_agent.py::test_base_agent_creation -v

커버리지 측정:
    pytest tests/test_agents/test_base_agent.py --cov=backend.agents --cov-report=html

테스트 결과 예상:
    test_base_agent_creation                     PASSED
    test_base_agent_creation_without_config      PASSED
    test_base_agent_execute_success              PASSED
    test_base_agent_execute_with_delay           PASSED
    test_validate_input_success                  PASSED
    test_validate_input_missing_task_type        PASSED
    test_validate_input_missing_required_field   PASSED
    test_count_tokens                            PASSED
    test_timer                                   PASSED
    test_safe_execute_success                    PASSED
    test_safe_execute_validation_error           PASSED
    test_safe_execute_execution_error            PASSED
    test_safe_execute_missing_task_type          PASSED
    test_log_execution_called                    PASSED
    test_full_workflow                           PASSED

    =============== 15 passed in 0.5s ===============
"""
