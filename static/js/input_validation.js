document.addEventListener('DOMContentLoaded', function () {
  const forms = [
    { form: document.getElementById('form1'), input: document.getElementById('input1') },
    { form: document.getElementById('form2'), input: document.getElementById('input2') }
  ];

  // 필터링할 단어 목록
  const forbiddenPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, // <script> 태그
    /<\/?[^>]+(>|$)/gi, // 기타 HTML 태그
    /alert\(/gi, // alert 함수 호출
    /on\w+=/gi // 이벤트 핸들러 속성
    // 여기에 추가로 필터링할 단어 또는 패턴을 추가할 수 있습니다.
  ];

  forms.forEach(({ form, input }) => {
    form.addEventListener('submit', function (event) {
      const inputValue = input.value;

      const isInvalid = forbiddenPatterns.some(pattern => pattern.test(inputValue));
      if (isInvalid) {
        alert('Invalid input: Certain words or patterns are not allowed.');
        event.preventDefault(); // 폼 제출 막기
      }
    });
  });
});