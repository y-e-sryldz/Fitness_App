function gonderMesaj() {
    var mesajInput = document.getElementById("mesaj");
    var mesajlarDiv = document.getElementById("mesajlar");

    var yeniMesaj = document.createElement("div");
    yeniMesaj.className = "mesaj-giden";
    yeniMesaj.innerHTML = "<strong>Sen:</strong> " + mesajInput.value;

    mesajlarDiv.appendChild(yeniMesaj);

    // Mesajı ekledikten sonra input'u temizle
    mesajInput.value = "";

    // Otomatik olarak en altta görünen mesajı görüntüle
    mesajlarDiv.scrollTop = mesajlarDiv.scrollHeight;
}
