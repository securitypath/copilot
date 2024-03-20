import 'https://gradio.s3-us-west-2.amazonaws.com/4.20.1/gradio.js';
import { hotjar } from 'react-hotjar';

export function unmount() {
    document.getElementById('evatutor-gradio-app')?.remove();
}

export interface ToolbarWidget {
    label: string;
    component: string;
}

export interface Identity {
    id: string;
}

interface DependencyContext {
    widgets: {
        addToolbarWidget: (widget: ToolbarWidget) => void;
    };
    identity: Identity;
}

hotjar.initialize(3898484, 6);
export function declareWidgets(dependencyContext: DependencyContext) {
    hotjar.identify(dependencyContext.identity.id, {});
    dependencyContext.widgets.addToolbarWidget({label: "EvaTutor", component: "<gradio-app id='evatutor-gradio-app' style=\"--background-fill-primary: #121212; --button-secondary-border-color: transparent; --embed-radius: 0; \" src=\"https://evatutor-space.sanchezcarlosjr.com/\"></gradio-app>"});
}
