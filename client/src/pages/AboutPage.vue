<script setup>
</script>
<template>
  <div class="container mt-5">
    <div class="text-center mb-5">
      <h1 class="display-3 fw-bold">Клуб «Инсайд»</h1>
      <h4 class="text-muted mt-2">Иркутск | Игра в мафию</h4>
      <p class="lead mt-4 mx-auto" style="max-width: 800px;">
        «ИНСАЙД» — место, где игра становится настоящей психологической борьбой.
        Здесь проверяют интуицию, логику и умение читать людей.
      </p>
      <router-link to="/sessions" class="btn btn-primary btn-lg mt-3 px-5 rounded-pill shadow-sm">Посмотреть расписание</router-link>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0 bg-light p-4 text-center">
          <h2 class="mb-3">📍</h2>
          <h4 class="fw-bold">Где мы находимся</h4>
          <p class="mb-0">г. Иркутск,<br>ул. Литвинова, 1</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0 bg-light p-4 text-center">
          <h2 class="mb-3">📅</h2>
          <h4 class="fw-bold">Когда играем</h4>
          <p class="mb-0">Каждый вторник, среду,<br>пятницу и воскресенье</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0 bg-light p-4 text-center">
          <h2 class="mb-3">💳</h2>
          <h4 class="fw-bold">Стоимость</h4>
          <p class="mb-0">Игровой вечер — 400р.<br><span class="text-success fw-bold">Для студентов — 270р.</span></p>
        </div>
      </div>
    </div>

    <div class="bg-white p-5 rounded-4 shadow-sm mb-5">
      <h3 class="text-center mb-4 fw-bold">Наши форматы игр</h3>
      <div class="row">
        <div class="col-md-6 mb-3">
          <div class="d-flex align-items-start">
            <span class="fs-3 me-3">🕵️</span>
            <div>
              <h5 class="mb-1">Спортивная мафия</h5>
              <p class="text-muted small mb-0">Классический турнирный формат для опытных игроков.</p>
            </div>
          </div>
        </div>
        <div class="col-md-6 mb-3">
          <div class="d-flex align-items-start">
            <span class="fs-3 me-3">🎭</span>
            <div>
              <h5 class="mb-1">Городская мафия</h5>
              <p class="text-muted small mb-0">Лёгкая и атмосферная игра для компаний и праздников.</p>
            </div>
          </div>
        </div>
        <div class="col-md-6 mb-3">
          <div class="d-flex align-items-start">
            <span class="fs-3 me-3">👶</span>
            <div>
              <h5 class="mb-1">Детская мафия</h5>
              <p class="text-muted small mb-0">Специальные сценарии для детей и подростков.</p>
            </div>
          </div>
        </div>
        <div class="col-md-6 mb-3">
          <div class="d-flex align-items-start">
            <span class="fs-3 me-3">🧩</span>
            <div>
              <h5 class="mb-1">Мафия для новичков</h5>
              <p class="text-muted small mb-0">Научим играть с нуля. Объясним правила и роли.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="text-center mb-5">
      <p class="lead mt-4 mx-auto" style="max-width: 800px;">Уютная атмосфера, профессиональные ведущие и сильное игровое комьюнити.</p>
      <p class="lead mt-4 mx-auto" style="max-width: 800px;">Если ты любишь психологию, азарт и живое общение — тебе точно к нам.</p>
      <p class="lead mt-4 mx-auto" style="max-width: 800px;">📩 Запись на игры — через бронирование на сайте.</p>
      <p class="lead mt-4 mx-auto" style="max-width: 800px;">Не забудьте включить уведомления, чтобы не пропустить анонсы! 🔥</p>
      <p class="lead mt-4 mx-auto" style="max-width: 800px;">INSIDE — почувствуй игру изнутри.</p>
    </div>
  </div>
</template>