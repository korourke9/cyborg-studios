/* Cyborg Phaser SDK — constrained facade for IR + LLM game scripts.
 * Loaded only inside the sandboxed playframe.
 */
(function (global) {
  "use strict";

  function destroyExisting() {
    if (global.__cyborgGame) {
      try {
        global.__cyborgGame.destroy(true);
      } catch (_err) {
        /* ignore */
      }
      global.__cyborgGame = null;
    }
  }

  function notify(type, extra) {
    if (global.parent && global.parent !== global) {
      global.parent.postMessage(Object.assign({ type: type }, extra || {}), "*");
    }
  }

  function hexColor(hex, fallback) {
    try {
      return Phaser.Display.Color.HexStringToColor(hex || fallback).color;
    } catch (_e) {
      return Phaser.Display.Color.HexStringToColor(fallback).color;
    }
  }

  /**
   * Trusted platformer builder. Level object may include authored twists:
   * - movingHazards: [{x,y,w,h,axis:'x'|'y',min,max,speed}]
   * - enemies: [{x,y,w,h,minX,maxX,speed}]
   * - doubleJump: boolean
   * - maxTimeSec: number (0 = off)
   * - requireAllCollectibles: boolean
   */
  function createPlatformerFromLevel(L) {
    const root = document.getElementById("game-root");
    if (!root || typeof Phaser === "undefined") {
      throw new Error("Phaser or #game-root missing");
    }
    const WIDTH = L.worldWidth || 800;
    const HEIGHT = L.worldHeight || 450;
    const VIEW_W = Math.min(800, WIDTH);
    const VIEW_H = Math.min(450, HEIGHT);
    const MOVE = L.move || 200;
    const JUMP = L.jump || -380;
    const GRAVITY = L.gravity || 1100;
    const platforms = L.platforms || [];
    const hazards = L.hazards || [];
    const movingHazards = L.movingHazards || [];
    const enemies = L.enemies || [];
    const collectibles = L.collectibles || [];
    const goal = L.goal;
    const SPAWN = { x: L.playerStartX || 80, y: L.playerStartY || 340 };
    const TEXTURES = L.textures || {};
    const HERO_W = L.heroDisplayW || 28;
    const HERO_H = L.heroDisplayH || 32;
    const HAZARD_W = L.hazardDisplayW || 32;
    const HAZARD_H = L.hazardDisplayH || 32;
    const GEM_W = L.collectibleDisplayW || 20;
    const GEM_H = L.collectibleDisplayH || 20;
    const NEED_COLLECT_ALL =
      L.requireAllCollectibles === undefined
        ? collectibles.length > 0
        : !!L.requireAllCollectibles;
    const DOUBLE_JUMP = !!L.doubleJump;
    const MAX_TIME = Number(L.maxTimeSec) || 0;

    class MainScene extends Phaser.Scene {
      constructor() {
        super("main");
        this.won = false;
        this.collected = 0;
        this.collectibleTotal = collectibles.length;
        this.jumpsRemaining = DOUBLE_JUMP ? 2 : 1;
        this.timeLeft = MAX_TIME;
      }

      preload() {
        if (TEXTURES.hero) this.load.image("hero", TEXTURES.hero);
        if (TEXTURES.backdrop) this.load.image("backdrop", TEXTURES.backdrop);
        if (TEXTURES.hazard) this.load.image("hazard", TEXTURES.hazard);
        if (TEXTURES.platform) this.load.image("platform", TEXTURES.platform);
        if (TEXTURES.collectible) this.load.image("collectible", TEXTURES.collectible);
      }

      create() {
        this.cameras.main.setBackgroundColor(L.backgroundHex || "#1a1424");
        this.cameras.main.setBounds(0, 0, WIDTH, HEIGHT);
        this.physics.world.setBounds(0, 0, WIDTH, HEIGHT);

        if (this.textures.exists("backdrop")) {
          this.add
            .image(WIDTH / 2, HEIGHT / 2, "backdrop")
            .setDisplaySize(WIDTH, HEIGHT)
            .setDepth(-10);
        }

        this.add
          .text(16, 12, L.title || "Cyborg Game", {
            fontFamily: "monospace",
            fontSize: "14px",
            color: L.playerHex || "#9b7ed9",
          })
          .setScrollFactor(0)
          .setDepth(20);

        this.statusText = this.add
          .text(16, 32, "", {
            fontFamily: "monospace",
            fontSize: "12px",
            color: L.goalHex || "#ff8c42",
          })
          .setScrollFactor(0)
          .setDepth(20);
        this._refreshStatus();

        const solids = this.physics.add.staticGroup();
        platforms.forEach(function (p) {
          let block;
          if (this.textures.exists("platform")) {
            block = this.add.tileSprite(p.x, p.y, p.w, p.h, "platform");
          } else {
            block = this.add.rectangle(
              p.x,
              p.y,
              p.w,
              p.h,
              hexColor(L.platformHex, "#3a2a4a"),
            );
          }
          this.physics.add.existing(block, true);
          solids.add(block);
        }, this);

        const hazardGroup = this.physics.add.staticGroup();
        hazards.forEach(function (h) {
          let body;
          if (this.textures.exists("hazard")) {
            body = this.add
              .image(h.x, h.y, "hazard")
              .setDisplaySize(h.w || HAZARD_W, h.h || HAZARD_H);
          } else {
            body = this.add.rectangle(
              h.x,
              h.y,
              h.w || HAZARD_W,
              h.h || HAZARD_H,
              0xc45c26,
            );
          }
          this.physics.add.existing(body, true);
          hazardGroup.add(body);
        }, this);

        this.movingHazardBodies = [];
        movingHazards.forEach(function (h) {
          const body = this.add.rectangle(
            h.x,
            h.y,
            h.w || 28,
            h.h || 28,
            0xe85d4c,
          );
          this.physics.add.existing(body, true);
          hazardGroup.add(body);
          this.movingHazardBodies.push({
            body: body,
            axis: h.axis === "y" ? "y" : "x",
            min: h.min,
            max: h.max,
            speed: h.speed || 70,
            dir: 1,
          });
        }, this);

        this.enemyBodies = [];
        enemies.forEach(function (e) {
          const sprite = this.add.rectangle(
            e.x,
            e.y,
            e.w || 24,
            e.h || 24,
            0x9b3d3d,
          );
          this.physics.add.existing(sprite);
          sprite.body.setAllowGravity(false);
          sprite.body.setImmovable(true);
          this.enemyBodies.push({
            body: sprite,
            minX: e.minX != null ? e.minX : e.x - 60,
            maxX: e.maxX != null ? e.maxX : e.x + 60,
            speed: e.speed || 60,
            dir: 1,
          });
        }, this);

        this.collectibleGroup = this.physics.add.staticGroup();
        collectibles.forEach(function (c) {
          let gem;
          if (this.textures.exists("collectible")) {
            gem = this.add
              .image(c.x, c.y, "collectible")
              .setDisplaySize(c.w || GEM_W, c.h || GEM_H);
          } else {
            gem = this.add.rectangle(
              c.x,
              c.y,
              c.w || GEM_W,
              c.h || GEM_H,
              hexColor(L.goalHex, "#ff8c42"),
            );
          }
          this.physics.add.existing(gem, true);
          this.collectibleGroup.add(gem);
        }, this);

        const goalRect = this.add.rectangle(
          goal.x,
          goal.y,
          goal.w,
          goal.h,
          hexColor(L.goalHex, "#ff8c42"),
        );
        this.physics.add.existing(goalRect, true);
        this.goalBody = goalRect;

        if (this.textures.exists("hero")) {
          this.player = this.physics.add.image(SPAWN.x, SPAWN.y, "hero");
          this.player.setDisplaySize(HERO_W, HERO_H);
          this.player.body.setSize(HERO_W * 0.7, HERO_H * 0.85);
        } else {
          this.player = this.add.rectangle(
            SPAWN.x,
            SPAWN.y,
            Math.max(20, HERO_W - 4),
            Math.max(24, HERO_H - 4),
            hexColor(L.playerHex, "#9b7ed9"),
          );
          this.physics.add.existing(this.player);
        }
        this.player.body.setCollideWorldBounds(true);
        this.cameras.main.startFollow(this.player, true, 0.12, 0.12);

        this.physics.add.collider(this.player, solids, function () {
          if (this.player.body.blocked.down) {
            this.jumpsRemaining = DOUBLE_JUMP ? 2 : 1;
          }
        }, null, this);
        this.physics.add.overlap(this.player, hazardGroup, this._fail, null, this);
        this.enemyBodies.forEach(function (entry) {
          this.physics.add.overlap(this.player, entry.body, this._fail, null, this);
        }, this);
        this.physics.add.overlap(
          this.player,
          this.collectibleGroup,
          function (_p, gem) {
            this._collect(gem);
          },
          null,
          this,
        );
        this.physics.add.overlap(this.player, this.goalBody, this._tryWin, null, this);

        this.cursors = this.input.keyboard.createCursorKeys();
        this.wasd = this.input.keyboard.addKeys("W,A,S,D,SPACE");
        this.jumpLatch = false;
        this.banner = this.add
          .text(VIEW_W / 2, VIEW_H / 2, "", {
            fontFamily: "monospace",
            fontSize: "22px",
            color: L.goalHex || "#ff8c42",
          })
          .setOrigin(0.5)
          .setScrollFactor(0)
          .setDepth(30);

        if (MAX_TIME > 0) {
          this.time.addEvent({
            delay: 1000,
            loop: true,
            callback: function () {
              if (this.won) return;
              this.timeLeft -= 1;
              this._refreshStatus();
              if (this.timeLeft <= 0) this._fail(true);
            },
            callbackScope: this,
          });
        }

        notify("cyborg-play-ready", { runtime: "sdk" });
      }

      _refreshStatus() {
        if (!this.statusText) return;
        const parts = [];
        if (this.collectibleTotal > 0) {
          parts.push("Gems " + this.collected + "/" + this.collectibleTotal);
        }
        if (MAX_TIME > 0) parts.push("Time " + Math.max(0, this.timeLeft));
        if (DOUBLE_JUMP) parts.push("2x jump");
        if (!parts.length) parts.push("Reach the goal · avoid hazards");
        this.statusText.setText(parts.join(" · "));
      }

      _collect(gem) {
        if (!gem.active) return;
        gem.destroy();
        this.collected += 1;
        this._refreshStatus();
      }

      _fail(fromTimer) {
        if (this.won) return;
        this.player.body.reset(SPAWN.x, SPAWN.y);
        this.jumpsRemaining = DOUBLE_JUMP ? 2 : 1;
        if (fromTimer === true) {
          this.timeLeft = MAX_TIME;
          this.banner.setText("TIME");
        } else {
          this.banner.setText("OUCH");
        }
        this.time.delayedCall(500, () => {
          if (!this.won) this.banner.setText("");
        });
        this._refreshStatus();
      }

      _tryWin() {
        if (this.won) return;
        if (NEED_COLLECT_ALL && this.collected < this.collectibleTotal) {
          this.banner.setText("NEED GEMS");
          this.time.delayedCall(600, () => {
            if (!this.won) this.banner.setText("");
          });
          return;
        }
        this.won = true;
        this.banner.setText("CLEAR");
        this.player.body.setVelocity(0, 0);
        notify("cyborg-play-clear", { runtime: "sdk" });
      }

      update(_time, delta) {
        if (this.won || !this.player) return;

        this.movingHazardBodies.forEach(function (m) {
          const pos = m.axis === "y" ? m.body.y : m.body.x;
          let next = pos + m.dir * m.speed * (delta / 1000);
          if (next > m.max) {
            next = m.max;
            m.dir = -1;
          } else if (next < m.min) {
            next = m.min;
            m.dir = 1;
          }
          if (m.axis === "y") {
            m.body.y = next;
            m.body.body.updateFromGameObject();
          } else {
            m.body.x = next;
            m.body.body.updateFromGameObject();
          }
        });

        this.enemyBodies.forEach(function (e) {
          let next = e.body.x + e.dir * e.speed * (delta / 1000);
          if (next > e.maxX) {
            next = e.maxX;
            e.dir = -1;
          } else if (next < e.minX) {
            next = e.minX;
            e.dir = 1;
          }
          e.body.x = next;
          e.body.body.reset(next, e.body.y);
        });

        const body = this.player.body;
        const left = this.cursors.left.isDown || this.wasd.A.isDown;
        const right = this.cursors.right.isDown || this.wasd.D.isDown;
        const jumpHeld =
          this.cursors.up.isDown ||
          this.cursors.space.isDown ||
          this.wasd.W.isDown ||
          this.wasd.SPACE.isDown;
        body.setVelocityX(0);
        if (left) body.setVelocityX(-MOVE);
        if (right) body.setVelocityX(MOVE);
        if (jumpHeld && !this.jumpLatch && this.jumpsRemaining > 0) {
          body.setVelocityY(JUMP);
          this.jumpsRemaining -= 1;
          this.jumpLatch = true;
        }
        if (!jumpHeld) this.jumpLatch = false;
        if (this.player.y > HEIGHT + 80) this._fail();
      }
    }

    destroyExisting();
    global.__cyborgGame = new Phaser.Game({
      type: Phaser.AUTO,
      parent: "game-root",
      width: VIEW_W,
      height: VIEW_H,
      backgroundColor: L.backgroundHex || "#1a1424",
      physics: {
        default: "arcade",
        arcade: { gravity: { y: GRAVITY }, debug: false },
      },
      scene: [MainScene],
      scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    });
  }

  /**
   * Entry for IR-template and LLM scripts.
   * callback receives { createPlatformerFromLevel, Phaser, notify }
   */
  function boot(callback) {
    if (typeof callback !== "function") {
      throw new Error("Cyborg.boot requires a function");
    }
    const api = {
      Phaser: global.Phaser,
      createPlatformerFromLevel: createPlatformerFromLevel,
      notify: notify,
      destroyExisting: destroyExisting,
    };
    callback(api);
  }

  global.Cyborg = { boot: boot, createPlatformerFromLevel: createPlatformerFromLevel };
})(window);
