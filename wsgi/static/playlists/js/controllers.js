var PlaylistControllers = angular.module('PlaylistControllers', []);

PlaylistControllers.controller('PlaylistCtrl', ['$scope', '$dragon', function ($scope, $dragon) {
    $scope.playlist = {};
    $scope.videos = [];
    $scope.channel = 'playlists';

    $dragon.onReady(function() {
        var PlaylistID = $('#videos-list').attr('data-id');

        $dragon.subscribe('video', $scope.channel, {playlist__id: PlaylistID}).then(function(response) {
            $scope.dataMapper = new DataMapper(response.data);
        });

        $dragon.getSingle('playlist', {id:PlaylistID}).then(function(response) {
            $scope.playlist = response.data;
        });

        $dragon.getList('video', {list_id:PlaylistID}).then(function(response) {
            $scope.videos = response.data;
        });
    });

    $dragon.onChannelMessage(function(channels, message) {
        if (indexOf.call(channels, $scope.channel) > -1) {
            $scope.$apply(function() {
                $scope.dataMapper.mapData($scope.videos, message);
            });
        }
    });

    // $scope.itemDone = function(item) {
    //     item.done = true != item.done;
    //     $dragon.update('todo-item', item);
    // }
}]);