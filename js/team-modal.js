/**
 * Team Member Modal Component
 * Handles displaying team member details in a modal dialog
 */

class TeamModal {
  constructor() {
    this.modal = null;
    this.modalContent = null;
    this.modalName = null;
    this.modalRole = null;
    this.modalBio = null;
    this.modalPhoto = null;
    this.closeBtn = null;
    this.overlay = null;
    this.lastFocused = null;
    this.init();
  }

  init() {
    // Create modal structure
    this.createModal();
    // Attach event listeners
    this.attachEventListeners();
  }

  createModal() {
    // Create modal overlay
    this.overlay = document.createElement("div");
    this.overlay.className = "team-modal-overlay";
    this.overlay.setAttribute("aria-hidden", "true");

    // Create modal container
    this.modal = document.createElement("div");
    this.modal.className = "team-modal";
    this.modal.setAttribute("role", "dialog");
    this.modal.setAttribute("aria-labelledby", "team-modal-name");
    this.modal.setAttribute("aria-modal", "true");

    // Create modal content
    this.modalContent = document.createElement("div");
    this.modalContent.className = "team-modal-content";

    // Create close button
    this.closeBtn = document.createElement("button");
    this.closeBtn.className = "team-modal-close";
    this.closeBtn.setAttribute("aria-label", "Close modal");
    this.closeBtn.innerHTML = '<i class="bi bi-x"></i>';

    // Create header
    const modalHeader = document.createElement("div");
    modalHeader.className = "team-modal-header";

    // Headshot slot. Replaced per card in open(): an <img> when the card has a
    // photo, an initials disc when it does not.
    this.modalPhoto = document.createElement("span");
    this.modalPhoto.className = "team-modal-photo team-modal-photo--initials";
    this.modalPhoto.setAttribute("aria-hidden", "true");

    // Name and role stack beside the headshot
    const modalHeaderText = document.createElement("div");
    modalHeaderText.className = "team-modal-header-text";

    // Create name element
    this.modalName = document.createElement("h2");
    this.modalName.className = "team-modal-name";
    this.modalName.id = "team-modal-name";

    // Create role element
    this.modalRole = document.createElement("p");
    this.modalRole.className = "team-modal-role";

    modalHeaderText.appendChild(this.modalName);
    modalHeaderText.appendChild(this.modalRole);

    modalHeader.appendChild(this.modalPhoto);
    modalHeader.appendChild(modalHeaderText);
    modalHeader.appendChild(this.closeBtn);

    // Create HR separator
    this.modalHr = document.createElement("hr");
    this.modalHr.className = "team-modal-hr";
    this.modalHr.style.display = "none";

    // Create bio element
    this.modalBio = document.createElement("div");
    this.modalBio.className = "team-modal-bio";

    // Assemble modal
    this.modalContent.appendChild(modalHeader);
    this.modalContent.appendChild(this.modalHr);
    this.modalContent.appendChild(this.modalBio);
    this.modal.appendChild(this.modalContent);
    this.overlay.appendChild(this.modal);

    // Add to body
    document.body.appendChild(this.overlay);
  }

  attachEventListeners() {
    // Close on overlay click
    this.overlay.addEventListener("click", (e) => {
      if (e.target === this.overlay) {
        this.close();
      }
    });

    // Close on close button click
    this.closeBtn.addEventListener("click", () => {
      this.close();
    });

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.isOpen()) {
        this.close();
      }
    });

    // Attach click handlers to team cards
    this.attachCardListeners();
  }

  attachCardListeners() {
    const teamCards = document.querySelectorAll(".team-card");
    teamCards.forEach((card) => {
      // Make card clickable
      card.style.cursor = "pointer";
      card.setAttribute("tabindex", "0");
      card.setAttribute("role", "button");

      card.addEventListener("click", (e) => {
        // Don't open if clicking on a link or button inside
        if (e.target.tagName === "A" || e.target.tagName === "BUTTON") {
          return;
        }
        this.open(card);
      });

      // Support keyboard navigation
      card.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          this.open(card);
        }
      });
    });
  }

  open(card) {
    // Extract data from card
    const name =
      card.querySelector(".team-card-name")?.textContent.trim() || "";
    const role =
      card.querySelector(".team-card-role")?.textContent.trim() || "";
    const bioElement = card.querySelector(".visually-hidden");

    // Get bio paragraphs
    let bioHTML = "";
    if (bioElement) {
      const paragraphs = bioElement.querySelectorAll("p");
      paragraphs.forEach((p) => {
        bioHTML += `<p>${p.textContent}</p>`;
      });
    }

    // Populate modal
    this.modalName.textContent = name;
    this.modalRole.textContent = role;
    this.modalBio.innerHTML = bioHTML;
    this.setPhoto(card, name);

    // Show HR only if there's bio content
    if (bioHTML.trim().length > 0) {
      this.modalHr.style.display = "block";
    } else {
      this.modalHr.style.display = "none";
    }

    // Show modal
    this.overlay.setAttribute("aria-hidden", "false");
    this.overlay.classList.add("team-modal-open");
    document.body.style.overflow = "hidden"; // Prevent body scroll

    // Focus management: remember the opener so close() can restore focus.
    this.lastFocused = card;
    this.focusCloseButton();
  }

  /**
   * Move focus into the dialog. Tried synchronously, then retried on the next
   * task: the overlay animates in from visibility:hidden, and a click's own
   * default action can focus the card afterwards, either of which would leave
   * focus outside the dialog.
   */
  focusCloseButton() {
    const attempt = () => {
      if (!this.isOpen()) return true;
      this.closeBtn.focus();
      return document.activeElement === this.closeBtn;
    };
    if (attempt()) return;
    setTimeout(attempt, 0);
  }

  /**
   * Show the card's headshot at modal size, or an initials disc when the card
   * has no photo. Swaps the element so an <img> is never left with no src.
   */
  setPhoto(card, name) {
    const cardImg = card.querySelector("img.team-card-photo");
    let next;

    if (cardImg && cardImg.getAttribute("src")) {
      next = document.createElement("img");
      next.className = "team-modal-photo";
      next.src = cardImg.getAttribute("src");
      next.alt = "";
      next.width = 96;
      next.height = 96;
    } else {
      next = document.createElement("span");
      next.className = "team-modal-photo team-modal-photo--initials";
      next.textContent = this.initialsFor(name);
    }
    next.setAttribute("aria-hidden", "true");

    this.modalPhoto.replaceWith(next);
    this.modalPhoto = next;
  }

  /** First letters of the first and last name parts, e.g. "Susan Michie" -> "SM". */
  initialsFor(name) {
    const parts = name.split(/\s+/).filter((w) => /[A-Za-z]/.test(w));
    if (!parts.length) return "";
    const first = parts[0][0];
    const last = parts.length > 1 ? parts[parts.length - 1][0] : "";
    return (first + last).toUpperCase();
  }

  close() {
    this.overlay.setAttribute("aria-hidden", "true");
    this.overlay.classList.remove("team-modal-open");
    document.body.style.overflow = ""; // Restore body scroll

    // Return focus to the card that opened the modal. Looking for
    // ".team-card:focus" here never matched, because open() had already moved
    // focus to the close button, so the opener is recorded instead.
    if (this.lastFocused && document.contains(this.lastFocused)) {
      this.lastFocused.focus();
    }
    this.lastFocused = null;
  }

  isOpen() {
    return this.overlay.classList.contains("team-modal-open");
  }
}

// Initialize modal when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    new TeamModal();
  });
} else {
  new TeamModal();
}
