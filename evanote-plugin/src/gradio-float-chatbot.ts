import 'https://gradio.s3-us-west-2.amazonaws.com/4.19.2/gradio.js';
export function unmount() {}


export function declareWidgets(obj: { addToolbarWidget: any }) {
    obj.addToolbarWidget({label: "EvaTutor", component: "<gradio-app style=\"--background-fill-primary: #121212; --button-secondary-border-color: transparent; --embed-radius: 0; \" src=\"https://evatutor-space.sanchezcarlosjr.com/\"></gradio-app>"});
}
