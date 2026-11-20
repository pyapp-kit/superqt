// Gallery cards: restart a card's animation from its first frame whenever the
// mouse enters the card. (An animated image keeps playing while it's hidden, so
// otherwise it would pick up wherever it happened to be.) The listener is on the
// document, so that it keeps working across instant navigation.
document.addEventListener("mouseover", (event) => {
  const card = event.target.closest?.(".sq-card");
  if (!card || card.contains(event.relatedTarget)) return;
  for (const img of card.querySelectorAll(".sq-card__anim")) {
    const src = img.getAttribute("src");
    img.setAttribute("src", "");
    img.setAttribute("src", src);
  }
});
