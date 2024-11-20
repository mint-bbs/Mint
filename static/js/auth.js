function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" +
        name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") +
        "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

document.addEventListener("DOMContentLoaded", () => {
  if (getCookie("2ch_X") !== undefined) {
    document.querySelector(".container").innerHTML = `
        <h1 class="title">あなたは認証済みです。</h1>
        <p class="subtitle">あなたのトークンは以下のとおりです。</p>
        <p>専ブラや、Cookieを保持できないブラウザでは、以下のトークンをメール欄に貼り付けてください。</p>
        <p class="has-text-danger">トークンは紛失したり、流失しないように厳重に管理してください！アカウントにログインできなくなったり、他人にアカウントを操作されたりしてしまいます！</p>
        <input type="text" value="#${getCookie("2ch_X")}" disabled />
    `;
  }
});

function callback(token) {
  console.log(token);
  fetch("/api/auth", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ token: token }),
  }).then((response) => {
    response.json().then((jsonData) => {
      console.log(jsonData);
      if (jsonData.detail == "success") {
        let date = new Date();
        date.setTime(date.getTime() + 100 * 365 * 24 * 60 * 60 * 1000);
        let expires = "expires=" + date.toUTCString();
        document.cookie = `2ch_X=${jsonData.code};${expires};path=/`;
        document.querySelector(".container").innerHTML = `
                <h1 class="title">認証成功</h1>
                <p class="subtitle">認証に成功しました。</p>
                <p>専ブラや、Cookieを保持できないブラウザでは、以下のトークンをメール欄に貼り付けてください。</p>
                <p class="has-text-danger">トークンは紛失したり、流失しないように厳重に管理してください！アカウントにログインできなくなったり、他人にアカウントを操作されたりしてしまいます！</p>
                <input type="text" value="#${jsonData.code}" disabled />
                <p>アカウントIDは以下のとおりです。</p>
                <input type="text" value="${jsonData.account_id}" disabled />
            `;
      } else {
        document.querySelector(".container").innerHTML = `
                <h1 class="title">認証失敗</h1>
                <p class="subtitle">認証に失敗しました。</p>
                <p>ページをリロードして、もう一度やり直してください。</p>
            `;
      }
    });
  });
}
