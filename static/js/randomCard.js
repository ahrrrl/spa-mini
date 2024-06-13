document.addEventListener('DOMContentLoaded', function () {
  const cardCount = 3; // 한 번에 표시할 이미지 수
  let currentIndex = 0; // 현재 인덱스

  function fetchRandomCards(startIndex) {
    fetch(`/random_song/?start=${startIndex}&count=${cardCount}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          for (let i = 0; i < cardCount; i++) {
            const index = startIndex + i;
            const card = data[i];
            if (card) {
              document.getElementById(`randomYoutubeTitle${i + 1}`).innerText =
                card.title;
              document.getElementById(`randomYoutubeArtist${i + 1}`).innerText =
                card.artist;
              document.getElementById(`randomYoutubeImage${i + 1}`).src =
                card.image_url;
              document.getElementById(`randomYoutubeLink${i + 1}`).href =
                card.link_url;
            } else {
              // 데이터가 없을 경우 처리
              document.getElementById(`randomYoutubeTitle${i + 1}`).innerText =
                '';
              document.getElementById(`randomYoutubeArtist${i + 1}`).innerText =
                '';
              document.getElementById(`randomYoutubeImage${i + 1}`).src = '';
              document.getElementById(`randomYoutubeLink${i + 1}`).href = '';
            }
          }
        }
      })
      .catch((error) => console.error('Error:', error));
  }

  // 페이지 로드 시 즉시 데이터 가져오기
  fetchRandomCards(currentIndex);

  // 오른쪽 화살표 버튼 클릭 시 다음 이미지 세트 로드
  document.getElementById('nextButton').addEventListener('click', function () {
    currentIndex += cardCount;
    fetchRandomCards(currentIndex);
  });

  // 10초마다 데이터 가져오기
  setInterval(function () {
    currentIndex = 0; // 첫 페이지로 초기화
    fetchRandomCards(currentIndex);
  }, 10000); // 10000 밀리초 = 10초
});
