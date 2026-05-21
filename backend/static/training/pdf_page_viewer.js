/**
 * Постраничный просмотр PDF (PDF.js) с кэшем документов.
 */
(function (global) {
  "use strict";

  const PDFJS_VERSION = "3.11.174";
  const PDFJS_BASE = "https://cdn.jsdelivr.net/npm/pdfjs-dist@" + PDFJS_VERSION + "/build/";
  const pdfDocCache = Object.create(null);

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = resolve;
      s.onerror = function () {
        reject(new Error("Не удалось загрузить: " + src));
      };
      document.head.appendChild(s);
    });
  }

  function ensurePdfJs() {
    if (global.pdfjsLib) {
      global.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_BASE + "pdf.worker.min.js";
      return Promise.resolve();
    }
    return loadScript(PDFJS_BASE + "pdf.min.js").then(function () {
      if (!global.pdfjsLib) {
        throw new Error("pdfjsLib не найден после загрузки скрипта");
      }
      global.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_BASE + "pdf.worker.min.js";
    });
  }

  function debounce(fn, ms) {
    var t;
    return function () {
      var self = this;
      var args = arguments;
      clearTimeout(t);
      t = setTimeout(function () {
        fn.apply(self, args);
      }, ms);
    };
  }

  function getCachedPdf(pdfUrl) {
    if (!pdfDocCache[pdfUrl]) {
      pdfDocCache[pdfUrl] = ensurePdfJs().then(function () {
        return global.pdfjsLib.getDocument({ url: pdfUrl, withCredentials: false }).promise;
      });
    }
    return pdfDocCache[pdfUrl];
  }

  function PdfPageViewer(options) {
    this.pdfUrl = options.pdfUrl;
    this.canvas = options.canvas;
    this.wrap = options.wrap;
    this.loadingEl = options.loadingEl;
    this.pageLabelEl = options.pageLabelEl;
    this.btnPrev = options.btnPrev;
    this.btnNext = options.btnNext;
    this.btnFs = options.btnFs || null;
    this.fsTarget = options.fsTarget || null;
    this.onPageChange = options.onPageChange || function () {};
    this.initialPage = Math.max(1, parseInt(options.initialPage, 10) || 1);
    this.onReady = options.onReady || function () {};

    this.pdf = null;
    this.pageNum = 1;
    this.numPages = 0;
    this.rendering = false;
    this._resizeBound = null;
    this._fsBound = null;
    this._onPrev = null;
    this._onNext = null;
    this._onFs = null;
  }

  PdfPageViewer.prototype.destroy = function () {
    if (this._resizeBound) {
      window.removeEventListener("resize", this._resizeBound);
      this._resizeBound = null;
    }
    if (this._fsBound && this.fsTarget) {
      this.fsTarget.removeEventListener("fullscreenchange", this._fsBound);
      this._fsBound = null;
    }
    if (this.btnPrev && this._onPrev) {
      this.btnPrev.removeEventListener("click", this._onPrev);
    }
    if (this.btnNext && this._onNext) {
      this.btnNext.removeEventListener("click", this._onNext);
    }
    if (this.btnFs && this._onFs) {
      this.btnFs.removeEventListener("click", this._onFs);
    }
    this._onPrev = this._onNext = this._onFs = null;
    this.pdf = null;
  };

  PdfPageViewer.prototype._updateChrome = function () {
    if (this.pageLabelEl) {
      this.pageLabelEl.textContent = this.numPages
        ? this.pageNum + " / " + this.numPages
        : "— / —";
    }
    if (this.btnPrev) {
      this.btnPrev.disabled = this.pageNum <= 1;
    }
    if (this.btnNext) {
      this.btnNext.disabled = this.pageNum >= this.numPages;
    }
  };

  PdfPageViewer.prototype._renderPage = function () {
    var self = this;
    if (!this.pdf || this.rendering) return;
    this.rendering = true;
    this.pdf
      .getPage(this.pageNum)
      .then(function (page) {
        var canvas = self.canvas;
        var ctx = canvas.getContext("2d");
        var wrap = self.wrap;
        var w = wrap.clientWidth || 900;
        var h = wrap.clientHeight || 640;
        var base = page.getViewport({ scale: 1 });
        var scale = Math.min(w / base.width, h / base.height) * 0.98;
        var viewport = page.getViewport({ scale: scale });
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        return page.render({ canvasContext: ctx, viewport: viewport }).promise;
      })
      .then(function () {
        self.rendering = false;
        self._updateChrome();
        self.onPageChange(self.pageNum, self.numPages);
      })
      .catch(function (err) {
        self.rendering = false;
        console.error(err);
        if (self.loadingEl) {
          self.loadingEl.textContent = "Ошибка отрисовки: " + (err && err.message ? err.message : err);
          self.loadingEl.classList.remove("d-none");
        }
      });
  };

  PdfPageViewer.prototype.goPrev = function () {
    if (this.pageNum <= 1) return;
    this.pageNum -= 1;
    this._renderPage();
  };

  PdfPageViewer.prototype.goNext = function () {
    if (this.pageNum >= this.numPages) return;
    this.pageNum += 1;
    this._renderPage();
  };

  PdfPageViewer.prototype.toggleFullscreen = function () {
    var el = this.fsTarget;
    if (!el) return;
    if (!document.fullscreenElement) {
      el.requestFullscreen().catch(function () {});
    } else {
      document.exitFullscreen();
    }
  };

  PdfPageViewer.prototype.init = function () {
    var self = this;
    if (this.loadingEl) {
      this.loadingEl.textContent = "Загрузка PDF…";
      this.loadingEl.classList.remove("d-none");
    }
    return getCachedPdf(this.pdfUrl)
      .then(function (pdf) {
        self.pdf = pdf;
        self.numPages = pdf.numPages;
        self.pageNum = Math.min(self.initialPage, self.numPages);
        if (self.loadingEl) {
          self.loadingEl.classList.add("d-none");
        }
        self._updateChrome();
        self._onPrev = function () { self.goPrev(); };
        self._onNext = function () { self.goNext(); };
        self._onFs = function () { self.toggleFullscreen(); };
        if (self.btnPrev) self.btnPrev.addEventListener("click", self._onPrev);
        if (self.btnNext) self.btnNext.addEventListener("click", self._onNext);
        if (self.btnFs) self.btnFs.addEventListener("click", self._onFs);
        self._resizeBound = debounce(function () {
          self._renderPage();
        }, 150);
        window.addEventListener("resize", self._resizeBound);
        if (self.fsTarget) {
          self._fsBound = debounce(function () {
            self._renderPage();
          }, 200);
          self.fsTarget.addEventListener("fullscreenchange", self._fsBound);
        }
        self._renderPage();
        self.onReady(self.numPages);
      })
      .catch(function (err) {
        console.error(err);
        if (self.loadingEl) {
          self.loadingEl.textContent =
            "Не удалось открыть PDF. Попробуйте «Скачать» или откройте в новой вкладке. " +
            (err && err.message ? err.message : "");
          self.loadingEl.classList.remove("d-none");
        }
        self.onReady(0);
      });
  };

  global.TrainingPdfPageViewer = PdfPageViewer;
  global.TrainingPdfDocCache = pdfDocCache;
})(typeof window !== "undefined" ? window : this);
