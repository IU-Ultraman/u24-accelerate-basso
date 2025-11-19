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
    this.closeBtn = null;
    this.overlay = null;
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

    // Create name element
    this.modalName = document.createElement("h2");
    this.modalName.className = "team-modal-name";
    this.modalName.id = "team-modal-name";

    // Create role element
    this.modalRole = document.createElement("p");
    this.modalRole.className = "team-modal-role";

    modalHeader.appendChild(this.modalName);
    modalHeader.appendChild(this.modalRole);
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

    // Focus management
    this.closeBtn.focus();
  }

  close() {
    this.overlay.setAttribute("aria-hidden", "true");
    this.overlay.classList.remove("team-modal-open");
    document.body.style.overflow = ""; // Restore body scroll

    // Return focus to the card that opened the modal
    const activeCard = document.querySelector(".team-card:focus");
    if (activeCard) {
      activeCard.focus();
    }
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
