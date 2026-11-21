<script setup>
</script>
<template>
  <div class="container mt-5 mb-5">
    <div class="text-center mb-5 py-5 bg-white rounded-4 shadow-sm">
      <h1 class="display-4 fw-bold mb-3">Клуб «Инсайд»</h1>
      <h5 class="text-secondary mb-4">Иркутск | Игра в мафию</h5>
      <p class="lead mx-auto text-muted" style="max-width: 700px;">
        «ИНСАЙД» — место, где игра становится настоящей психологической борьбой.
        Здесь проверяют интуицию, логику и умение читать людей.
      </p>
      <router-link to="/sessions" class="btn btn-dark btn-lg mt-4 px-5 rounded-pill">Посмотреть расписание</router-link>
    </div>

    <div class="row g-4 mb-5">
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0 bg-light p-4 text-center">
          <h4 class="fw-bold">Где мы находимся</h4>
          <p class="mb-0 text-muted">г. Иркутск,<br>ул. Литвинова, 1</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0 bg-light p-4 text-center">
          <h4 class="fw-bold">Когда играем</h4>
          <p class="mb-0 text-muted">Каждый вторник, среду,<br>пятницу и воскресенье</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0 bg-light p-4 text-center">
          <h4 class="fw-bold">Стоимость</h4>
          <p class="mb-0 text-muted">Игровой вечер — 400р.<br><span class="text-success fw-bold">Для студентов — 270р.</span></p>
        </div>
      </div>
    </div>

    <div class="bg-white p-5 rounded-4 shadow-sm mb-5">
      <h3 class="text-center mb-4 fw-bold">Наши форматы игр</h3>
      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="d-flex align-items-start">
              <h5 class="mb-1">Спортивная мафия</h5>
              <br>
              <p class="text-muted small mb-0">Классический турнирный формат для опытных игроков.</p>
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="d-flex align-items-start">
              <h5 class="mb-1">Городская мафия</h5>
              <br>
              <p class="text-muted small mb-0">Лёгкая и атмосферная игра для компаний и праздников.</p>
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="d-flex align-items-start">
              <h5 class="mb-1">Детская мафия</h5>
              <br>
              <p class="text-muted small mb-0">Специальные сценарии для детей и подростков.</p>
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="d-flex align-items-start">
              <h5 class="mb-1">Мафия для новичков</h5>
              <br>
              <p class="text-muted small mb-0">Научим играть с нуля. Объясним правила и роли.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>