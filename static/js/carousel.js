class Carousel {
  constructor(container, options = {}) {
    this.container = container;
    this.wrapper = container.querySelector('.carousel-wrapper');
    this.slides = container.querySelectorAll('.carousel-slide');
    this.prevBtn = container.querySelector('.carousel-prev');
    this.nextBtn = container.querySelector('.carousel-next');
    this.indicators = container.querySelectorAll('.carousel-indicator');
    this.caption = container.parentElement.querySelector('#carousel-caption');

    this.currentIndex = 0;
    this.totalSlides = this.slides.length;
    this.autoplay = options.autoplay !== undefined ? options.autoplay : true; // Default true
    this.autoplayInterval = null;
    this.intervalTime = 4000; // 4 seconds
    this.captions = JSON.parse(container.dataset.captions || '["", ""]');

    this.init();
  }

  init() {
    this.updateIndicators();
    this.addEventListeners();
    if (this.autoplay) {
      this.startAutoplay();
    }
  }

  addEventListeners() {
    // Button controls
    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', () => this.prev());
    }
    if (this.nextBtn) {
      this.nextBtn.addEventListener('click', () => this.next());
    }

    // Indicator controls
    this.indicators.forEach((indicator, index) => {
      indicator.addEventListener('click', () => this.goToSlide(index));
    });

    // Keyboard controls
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        this.prev();
      } else if (e.key === 'ArrowRight') {
        this.next();
      }
    });

    // Touch events
    this.wrapper.addEventListener('touchstart', (e) => this.handleTouchStart(e));
    this.wrapper.addEventListener('touchmove', (e) => this.handleTouchMove(e));
    this.wrapper.addEventListener('touchend', (e) => this.handleTouchEnd(e));

    // Mouse drag
    this.wrapper.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    document.addEventListener('mouseup', () => this.handleMouseUp());

    // Pause autoplay on hover/focus
    this.container.addEventListener('mouseenter', () => this.pauseAutoplay());
    this.container.addEventListener('mouseleave', () => this.resumeAutoplay());
    this.container.addEventListener('focusin', () => this.pauseAutoplay());
    this.container.addEventListener('focusout', () => this.resumeAutoplay());
  }

  goToSlide(index) {
    this.currentIndex = index;
    this.updateSlide();
    this.updateIndicators();
  }

  prev() {
    this.currentIndex = (this.currentIndex - 1 + this.totalSlides) % this.totalSlides;
    this.updateSlide();
    this.updateIndicators();
  }

  next() {
    this.currentIndex = (this.currentIndex + 1) % this.totalSlides;
    this.updateSlide();
    this.updateIndicators();
  }

  updateSlide() {
    const translateX = -this.currentIndex * 100;
    this.wrapper.style.transform = `translateX(${translateX}%)`;
  }

  updateIndicators() {
    this.indicators.forEach((indicator, index) => {
      indicator.classList.toggle('active', index === this.currentIndex);
    });
    this.updateCaption();
  }

  updateCaption() {
    if (this.caption) {
      this.caption.classList.add('fade-out');
      setTimeout(() => {
        this.caption.textContent = this.captions[this.currentIndex];
        this.caption.classList.remove('fade-out');
      }, 250);
    }
  }

  handleTouchStart(e) {
    this.startX = e.touches[0].clientX;
    this.isDragging = true;
  }

  handleTouchMove(e) {
    if (!this.isDragging) return;
    this.currentX = e.touches[0].clientX;
  }

  handleTouchEnd() {
    if (!this.isDragging) return;
    const diff = this.startX - this.currentX;
    if (Math.abs(diff) > this.dragThreshold) {
      if (diff > 0) {
        this.next();
      } else {
        this.prev();
      }
    }
    this.isDragging = false;
  }

  handleMouseDown(e) {
    this.startX = e.clientX;
    this.isDragging = true;
    this.wrapper.style.cursor = 'grabbing';
  }

  handleMouseMove(e) {
    if (!this.isDragging) return;
    this.currentX = e.clientX;
  }

  handleMouseUp() {
    if (!this.isDragging) return;
    const diff = this.startX - this.currentX;
    if (Math.abs(diff) > this.dragThreshold) {
      if (diff > 0) {
        this.next();
      } else {
        this.prev();
      }
    }
    this.isDragging = false;
    this.wrapper.style.cursor = 'grab';
  }

  startAutoplay() {
    this.autoplayInterval = setInterval(() => {
      this.next();
    }, this.intervalTime);
  }

  pauseAutoplay() {
    if (this.autoplayInterval) {
      clearInterval(this.autoplayInterval);
      this.autoplayInterval = null;
    }
  }

  resumeAutoplay() {
    if (this.autoplay && !this.autoplayInterval) {
      this.startAutoplay();
    }
  }

  toggleAutoplay() {
    this.autoplay = !this.autoplay;
    if (this.autoplay) {
      this.startAutoplay();
    } else {
      this.pauseAutoplay();
    }
  }
}

// Initialize carousels
document.addEventListener('DOMContentLoaded', () => {
  const carousels = document.querySelectorAll('.carousel-container');
  carousels.forEach(container => {
    const autoplay = container.dataset.autoplay === 'true';
    new Carousel(container, { autoplay });
  });
});