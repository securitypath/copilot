import {css, html, LitElement} from 'lit'
import {customElement, property} from 'lit/decorators.js'
import 'https://gradio.s3-us-west-2.amazonaws.com/4.15.0/gradio.js';

/**
 * Gradio Float ChatBot
 *
 */
@customElement('gradio-float-chatbot')
export class GradioFloatChatbot extends LitElement {
    @property({type: Boolean}) showChatBot = false;

    render() {
        return html`
            <li @click=${this._onClick} class="chatbot-toggle">EvaTutor</li>
            ${this.showChatBot ? html`
                <slot></slot>` : ""}
        `
    }

    private _onClick() {
        this.showChatBot = !this.showChatBot;
    }

    static styles = css`
      .chatbot-toggle {
            display: -webkit-inline-box;
    display: -webkit-inline-flex;
    display: -ms-inline-flexbox;
    display: inline-flex;
    -webkit-align-items: center;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    -webkit-justify-content: center;
    justify-content: center;
    position: relative;
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
    background-color: transparent;
    outline: 0;
    border: 0;
    margin: 0;
    border-radius: 0;
    padding: 0;
    cursor: pointer;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    vertical-align: middle;
    -moz-appearance: none;
    -webkit-appearance: none;
    -webkit-text-decoration: none;
    text-decoration: none;
    color: inherit;
    font-weight: 400;
    font-size: 1rem;
    line-height: 1.5;
    letter-spacing: 0.00938em;
    display: -webkit-box;
    display: -webkit-flex;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-pack: start;
    -ms-flex-pack: start;
    -webkit-justify-content: flex-start;
    justify-content: flex-start;
    -webkit-align-items: center;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    position: relative;
    -webkit-text-decoration: none;
    text-decoration: none;
    min-height: 48px;
    padding-top: 6px;
    padding-bottom: 6px;
    box-sizing: border-box;
    white-space: nowrap;
    padding-left: 16px;
    padding-right: 16px;
      }
      
      ::slotted(.chatbot) {
        border: 0;
        position: fixed;
        width: 30em;
        height: 54em;
        top: 1.5em;
        z-index: 2;
        right: 0.1em;
      }
    `
}

const id = "cicese-evatutor-chatbot";

function addElement(src: string) {
    const evanoteFloatChatBot = document.createElement("gradio-float-chatbot");
    evanoteFloatChatBot.id = id;
    const gradioApp = document.createElement("gradio-app");
    gradioApp.setAttribute('src', src);
    gradioApp.classList.add('chatbot');
    evanoteFloatChatBot.appendChild(gradioApp);
    const header = document.getElementById("header-flex-end");
    header?.prepend(evanoteFloatChatBot);
}

function removeElement() {
    const evanoteFloatChatBot = document.getElementById(id);
    evanoteFloatChatBot?.remove();
}

declare global {
    interface HTMLElementTagNameMap {
        'gradio-float-chatbot': GradioFloatChatbot
    }
}

export function mount() {
    addElement("https://e8015202808bbbdcb4.gradio.live");
}

export function unmount() {
    removeElement();
}