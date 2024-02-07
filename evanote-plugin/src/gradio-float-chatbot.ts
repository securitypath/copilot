import { LitElement, css, html } from 'lit'
import { customElement, property } from 'lit/decorators.js'
import avatar from './avatar.png';
import 'https://gradio.s3-us-west-2.amazonaws.com/4.15.0/gradio.js';

/**
 * Gradio Float ChatBot
 *
 */
@customElement('gradio-float-chatbot')
export class GradioFloatChatbot extends LitElement {
  @property({ type: Boolean })
  showChatBot = false;

  render() {
    return html`
      <img @click=${this._onClick}  src=${avatar} class="chatbot-toggle" alt="ChatBot Float" height="512" width="512" />
      ${this.showChatBot ? html`<slot></slot>` : ""}
    `
  }

  private _onClick() {
    this.showChatBot = !this.showChatBot;
  }

  static styles = css`
    .chatbot-toggle {
      position: fixed;
      bottom: 1em;
      right: 1.5em;
      width: 4em;
      height: 4em;
      background-color: #f1f1f1;
      border-radius: 20em;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      overflow: hidden;
      z-index: 3;
      cursor: pointer;
    }

    ::slotted(.chatbot) {
      border: 0;
      position: fixed;
      bottom: 0;
      right: 3em;
      width: 32em;
      height: 38.5em;
      z-index: 2;
    }
  `
}

function addElement(src: string) {
  const evanoteFloatChatBot = document.createElement("gradio-float-chatbot");
  const gradioApp = document.createElement("gradio-app");
  gradioApp.setAttribute('src', src);
  gradioApp.classList.add('chatbot');
  evanoteFloatChatBot.appendChild(gradioApp);
  document.body.appendChild(evanoteFloatChatBot);
}

declare global {
  interface HTMLElementTagNameMap {
    'gradio-float-chatbot': GradioFloatChatbot
  }
}

addElement("https://27dd768bce6de1b822.gradio.live");