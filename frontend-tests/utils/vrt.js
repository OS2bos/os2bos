import { t } from "testcafe"
import resemble from "resemblejs"
import fs from 'fs'

export default async function(testFixtureName, testName, testInfo) {

    const actual_img_path = `vrt-actual-img/${ testFixtureName }-${ testName }.png`,
          base_img_path = `vrt-base-img/${ testFixtureName }-${ testName }.png`

    const base_exists = fs.existsSync(`screenshots/${ base_img_path }`)

    await t.takeScreenshot({
        path: actual_img_path
    })
    
    const actual_exists = fs.existsSync(`screenshots/${ actual_img_path }`)

    if (actual_exists && base_exists) {
        await resemble(`screenshots/${ base_img_path }`)
        .compareTo(`screenshots/${ actual_img_path }`)
        .scaleToSameSize()
        .outputSettings({
            errorColor: {
                red: 255,
                green: 0,
                blue: 255
            },
            errorType: 'movement',
            transparency: 0.3,
            largeImageThreshold: 1200,
            useCrossOrigin: false,
            outputDiff: true
        })
        .onComplete(async img_data => {

            if (img_data.rawMisMatchPercentage > 0) {
                fs.writeFileSync(`screenshots/vrt-reported-img/${ testFixtureName }-${ testName }-diff.png`, img_data.getBuffer())
                throw new Error(`Visual mismatch detected in test. ${ testInfo }. Please check the report at ./screenshots/vrt-reported-img/${ testFixtureName }-${ testName }-diff.png.`)
            } else {
                console.log('This looks fine')
            }

        })
    }

    if (!base_exists) {
        await t.takeScreenshot({
            path: base_img_path
        })
        console.log('THERE WAS NO BASE IMAGE. NO VISUAL TESTING WAS PERFORMED.')
        console.log('Base image for later testing captured.')
    }

}