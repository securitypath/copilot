import 'https://gradio.s3-us-west-2.amazonaws.com/4.19.2/gradio.js';
export function unmount() {

}


export function declareWidgets(obj: { addToolbarWidget: any }) {
    obj.addToolbarWidget({
        label: "EvaNote", component: "<gradio-app src=\"https://evatutor-space.sanchezcarlosjr.com/\"></gradio-app>"
    });
}
