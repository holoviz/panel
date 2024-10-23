/*!
 * FilePondPluginFileValidateType 1.2.9
 * Licensed under MIT, https://opensource.org/licenses/MIT/
 * Please visit https://pqina.nl/filepond/ for details.
 */

/* eslint-disable */

(function(global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined'
        ? (module.exports = factory())
        : typeof define === 'function' && define.amd
        ? define(factory)
        : ((global = global || self), (global.FilePondPluginFileValidateType = factory()));
})(this, function() {
    'use strict';

    var plugin = function plugin(_ref) {
        var addFilter = _ref.addFilter,
            utils = _ref.utils;
        // get quick reference to Type utils
        var Type = utils.Type,
            isString = utils.isString,
            replaceInString = utils.replaceInString,
            guesstimateMimeType = utils.guesstimateMimeType,
            getExtensionFromFilename = utils.getExtensionFromFilename,
            getFilenameFromURL = utils.getFilenameFromURL;

        var mimeTypeMatchesWildCard = function mimeTypeMatchesWildCard(mimeType, wildcard) {
            var mimeTypeGroup = (/^[^/]+/.exec(mimeType) || []).pop(); // image/png -> image
            var wildcardGroup = wildcard.slice(0, -2); // image/* -> image
            return mimeTypeGroup === wildcardGroup;
        };

        var isValidMimeType = function isValidMimeType(acceptedTypes, userInputType) {
            return acceptedTypes.some(function(acceptedType) {
                // accepted is wildcard mime type
                if (/\*$/.test(acceptedType)) {
                    return mimeTypeMatchesWildCard(userInputType, acceptedType);
                }

                // is normal mime type
                return acceptedType === userInputType;
            });
        };

        var getItemType = function getItemType(item) {
            // if the item is a url we guess the mime type by the extension
            var type = '';
            if (isString(item)) {
                var filename = getFilenameFromURL(item);
                var extension = getExtensionFromFilename(filename);
                if (extension) {
                    type = guesstimateMimeType(extension);
                }
            } else {
                type = item.type;
            }

            return type;
        };

        var validateFile = function validateFile(item, acceptedFileTypes, typeDetector) {
            // no types defined, everything is allowed \o/
            if (acceptedFileTypes.length === 0) {
                return true;
            }

            // gets the item type
            var type = getItemType(item);

            // no type detector, test now
            if (!typeDetector) {
                return isValidMimeType(acceptedFileTypes, type);
            }

            // use type detector
            return new Promise(function(resolve, reject) {
                typeDetector(item, type)
                    .then(function(detectedType) {
                        if (isValidMimeType(acceptedFileTypes, detectedType)) {
                            resolve();
                        } else {
                            reject();
                        }
                    })
                    .catch(reject);
            });
        };

        var applyMimeTypeMap = function applyMimeTypeMap(map) {
            return function(acceptedFileType) {
                return map[acceptedFileType] === null
                    ? false
                    : map[acceptedFileType] || acceptedFileType;
            };
        };

        // setup attribute mapping for accept
        addFilter('SET_ATTRIBUTE_TO_OPTION_MAP', function(map) {
            return Object.assign(map, {
                accept: 'acceptedFileTypes',
            });
        });

        // filtering if an item is allowed in hopper
        addFilter('ALLOW_HOPPER_ITEM', function(file, _ref2) {
            var query = _ref2.query;
            // if we are not doing file type validation exit
            if (!query('GET_ALLOW_FILE_TYPE_VALIDATION')) {
                return true;
            }

            // we validate the file against the accepted file types
            return validateFile(file, query('GET_ACCEPTED_FILE_TYPES'));
        });

        // called for each file that is loaded
        // right before it is set to the item state
        // should return a promise
        addFilter('LOAD_FILE', function(file, _ref3) {
            var query = _ref3.query;
            return new Promise(function(resolve, reject) {
                if (!query('GET_ALLOW_FILE_TYPE_VALIDATION')) {
                    resolve(file);
                    return;
                }

                var acceptedFileTypes = query('GET_ACCEPTED_FILE_TYPES');

                // custom type detector method
                var typeDetector = query('GET_FILE_VALIDATE_TYPE_DETECT_TYPE');

                // if invalid, exit here
                var validationResult = validateFile(file, acceptedFileTypes, typeDetector);

                var handleRejection = function handleRejection() {
                    var acceptedFileTypesMapped = acceptedFileTypes
                        .map(
                            applyMimeTypeMap(
                                query('GET_FILE_VALIDATE_TYPE_LABEL_EXPECTED_TYPES_MAP')
                            )
                        )
                        .filter(function(label) {
                            return label !== false;
                        });

                    var acceptedFileTypesMappedUnique = acceptedFileTypesMapped.filter(function(
                        item,
                        index
                    ) {
                        return acceptedFileTypesMapped.indexOf(item) === index;
                    });

                    reject({
                        status: {
                            main: query('GET_LABEL_FILE_TYPE_NOT_ALLOWED'),
                            sub: replaceInString(
                                query('GET_FILE_VALIDATE_TYPE_LABEL_EXPECTED_TYPES'),
                                {
                                    allTypes: acceptedFileTypesMappedUnique.join(', '),
                                    allButLastType: acceptedFileTypesMappedUnique
                                        .slice(0, -1)
                                        .join(', '),
                                    lastType:
                                        acceptedFileTypesMappedUnique[
                                            acceptedFileTypesMappedUnique.length - 1
                                        ],
                                }
                            ),
                        },
                    });
                };

                // has returned new filename immidiately
                if (typeof validationResult === 'boolean') {
                    if (!validationResult) {
                        return handleRejection();
                    }
                    return resolve(file);
                }

                // is promise
                validationResult
                    .then(function() {
                        resolve(file);
                    })
                    .catch(handleRejection);
            });
        });

        // expose plugin
        return {
            // default options
            options: {
                // Enable or disable file type validation
                allowFileTypeValidation: [true, Type.BOOLEAN],

                // What file types to accept
                acceptedFileTypes: [[], Type.ARRAY],
                // - must be comma separated
                // - mime types: image/png, image/jpeg, image/gif
                // - extensions: .png, .jpg, .jpeg ( not enabled yet )
                // - wildcards: image/*

                // label to show when a type is not allowed
                labelFileTypeNotAllowed: ['File is of invalid type', Type.STRING],

                // nicer label
                fileValidateTypeLabelExpectedTypes: [
                    'Expects {allButLastType} or {lastType}',
                    Type.STRING,
                ],

                // map mime types to extensions
                fileValidateTypeLabelExpectedTypesMap: [{}, Type.OBJECT],

                // Custom function to detect type of file
                fileValidateTypeDetectType: [null, Type.FUNCTION],
            },
        };
    };

    // fire pluginloaded event if running in browser, this allows registering the plugin when using async script tags
    var isBrowser = typeof window !== 'undefined' && typeof window.document !== 'undefined';
    if (isBrowser) {
        document.dispatchEvent(new CustomEvent('FilePond:pluginloaded', { detail: plugin }));
    }

    return plugin;
});
